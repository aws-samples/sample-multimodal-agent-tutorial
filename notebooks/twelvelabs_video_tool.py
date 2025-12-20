"""
TwelveLabs Video Analysis Tool for Strands Agents

Simple tool for video analysis using TwelveLabs API.
Requires TL_API_KEY environment variable.
"""

import os
import json
from typing import Dict
from strands import tool

@tool
def twelvelabs_video_analysis(
    action: str,
    video_path: str = None,
    video_name: str = None,
    prompt: str = None,
    index_name: str = "video-analysis-index",
    temperature: float = 0.2
) -> Dict:
    """
    Video analysis using TwelveLabs API.
    
    Actions:
    - upload: Upload video (video_path=file/URL, video_name=name)
    - query: Ask about video (video_path=video_id, prompt=question)
    - list_videos: List all available videos
    
    Args:
        action: Operation to perform
        video_path: File path/URL for upload, video_id for query
        video_name: Video name (upload only)
        prompt: Question about video (query only)
        index_name: Index name for upload
        temperature: Model temperature
        
    Returns:
        Dict with operation results
    """
    
    # Validate API key
    api_key = os.environ.get('TL_API_KEY')
    if not api_key:
        return {"status": "error", "content": [{"text": "TL_API_KEY environment variable required"}]}
    
    try:
        if action == "upload":
            return _handle_upload(api_key, video_path, video_name, index_name)
        elif action == "query":
            return _handle_query(api_key, video_path, prompt, temperature)
        elif action == "list_videos":
            return _handle_list_videos(api_key)
        else:
            return {"status": "error", "content": [{"text": f"Invalid action: {action}. Use upload, query, or list_videos"}]}
    
    except Exception as e:
        return {"status": "error", "content": [{"text": f"Operation failed: {str(e)}"}]}

def _handle_upload(api_key: str, video_path: str, video_name: str, index_name: str) -> Dict:
    """Handle video upload to TwelveLabs."""
    
    if not video_path or not video_name:
        return {"status": "error", "content": [{"text": "video_path and video_name required for upload"}]}
    
    from twelvelabs import TwelveLabs
    from twelvelabs.indexes import IndexesCreateRequestModelsItem
    
    client = TwelveLabs(api_key=api_key)
    
    # Get or create index
    index = _get_or_create_index(client, index_name)
    
    # Upload video
    if video_path.startswith("http"):
        task = client.tasks.create(index_id=index.id, video_url=video_path)
    else:
        with open(video_path, "rb") as video_file:
            task = client.tasks.create(index_id=index.id, video_file=video_file)
    
    # Wait for completion
    task = client.tasks.wait_for_done(task_id=task.id)
    
    if task.status != "ready":
        return {"status": "error", "content": [{"text": f"Upload failed with status: {task.status}"}]}
    
    # Generate insights
    gist = client.gist(video_id=task.video_id, types=["title", "topic", "hashtag"])
    
    return {
        "status": "success",
        "content": [{
            "json": {
                "video_id": task.video_id,
                "title": gist.title,
                "topics": gist.topics,
                "hashtags": gist.hashtags
            }
        }]
    }

def _handle_query(api_key: str, video_path: str, prompt: str, temperature: float) -> Dict:
    """Handle video query using TwelveLabs API."""
    
    if not video_path or not prompt:
        return {"status": "error", "content": [{"text": "video_path (video_id) and prompt required for query"}]}
    
    import requests
    
    # Call analyze API
    response = requests.post(
        "https://api.twelvelabs.io/v1.3/analyze",
        json={
            "video_id": video_path,
            "prompt": prompt,
            "temperature": temperature
        },
        headers={"x-api-key": api_key},
        timeout=30
    )
    
    if response.status_code != 200:
        return {"status": "error", "content": [{"text": f"Query failed: {response.text}"}]}
    
    # Process streaming response
    text_parts = []
    for line in response.text.strip().split('\n'):
        if line.strip():
            try:
                event = json.loads(line)
                if event.get("event_type") == "text_generation":
                    text_parts.append(event.get("text", ""))
            except json.JSONDecodeError:
                continue
    
    return {
        "status": "success",
        "content": [{
            "json": {
                "video_id": video_path,
                "prompt": prompt,
                "response": "".join(text_parts)
            }
        }]
    }

def _handle_list_videos(api_key: str) -> Dict:
    """List all videos across all indexes."""
    
    import requests
    
    headers = {"x-api-key": api_key}
    
    # Get all indexes
    indexes_response = requests.get(
        "https://api.twelvelabs.io/v1.3/indexes",
        headers=headers,
        params={"model_family": "pegasus"},
        timeout=30
    )
    
    if indexes_response.status_code != 200:
        return {"status": "error", "content": [{"text": f"Failed to list indexes: {indexes_response.text}"}]}
    
    # Collect videos from all indexes
    all_videos = []
    indexes_data = indexes_response.json()
    
    for index in indexes_data.get("data", []):
        if index.get("video_count", 0) > 0:
            videos_response = requests.get(
                f"https://api.twelvelabs.io/v1.3/indexes/{index['_id']}/videos",
                headers=headers,
                timeout=30
            )
            
            if videos_response.status_code == 200:
                videos_data = videos_response.json()
                for video in videos_data.get("data", []):
                    all_videos.append({
                        "video_id": video["_id"],
                        "created_at": video.get("created_at"),
                        "index_name": index["index_name"],
                        "index_id": index["_id"]
                    })
    
    return {
        "status": "success",
        "content": [{
            "json": {
                "videos": all_videos,
                "total_count": len(all_videos)
            }
        }]
    }

def _get_or_create_index(client, index_name: str):
    """Get existing index or create new one."""
    
    from twelvelabs.indexes import IndexesCreateRequestModelsItem
    
    # Try to find existing index
    try:
        for index in client.indexes.list():
            if index.index_name == index_name:
                return index
    except Exception:
        pass
    
    # Create new index
    return client.indexes.create(
        index_name=index_name,
        models=[
            IndexesCreateRequestModelsItem(
                model_name="pegasus1.2",
                model_options=["visual", "audio"]
            )
        ]
    )
