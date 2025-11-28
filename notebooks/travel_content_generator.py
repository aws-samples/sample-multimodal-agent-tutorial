#!/usr/bin/env python3
"""
Travel Content Generator Application

Generate complete travel content packages (images, videos, and itineraries)
using Amazon Bedrock and Strands Agents.
"""

import os
import sys
import boto3
from strands import Agent
from strands.models import BedrockModel
from strands_tools import generate_image, file_write, nova_reels, use_aws


def get_user_input():
    """Get user input for content generation."""
    print("\n" + "="*80)
    print("🌍 Travel Content Generator")
    print("="*80)
    
    # Get destination details
    destination = input("\n📍 Enter destination (e.g., 'Barcelona, Spain'): ").strip()
    if not destination:
        print("❌ Destination is required")
        sys.exit(1)
    
    landmark = input("🏛️  Enter main landmark (e.g., 'Sagrada Familia'): ").strip()
    if not landmark:
        print("❌ Landmark is required")
        sys.exit(1)
    
    # Get trip duration
    while True:
        try:
            duration = int(input("📅 Enter trip duration in days (e.g., 5): ").strip())
            if duration > 0:
                break
            print("❌ Duration must be positive")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Get travel style
    print("\n🎨 Travel styles: cultural, romantic, adventure, modern, historic, luxury")
    style = input("   Enter travel style: ").strip().lower()
    if not style:
        style = "cultural"
    
    # Get season
    print("\n🌤️  Seasons: spring, summer, fall, winter")
    season = input("   Enter season: ").strip().lower()
    if not season:
        season = "summer"
    
    # Get S3 bucket for video generation
    print("\n📦 Video generation requires an S3 bucket (AWS Bedrock limitation)")
    print("   Leave empty to skip video generation")
    bucket = input("   Enter S3 bucket name: ").strip()
    
    # Ask if user wants to generate video
    generate_video = False
    if bucket:
        response = input(f"\n🎬 Generate video using bucket '{bucket}'? (y/n): ").strip().lower()
        generate_video = response in ['y', 'yes']
    
    return {
        'destination': destination,
        'landmark': landmark,
        'duration': duration,
        'style': style,
        'season': season,
        'bucket': bucket if generate_video else None,
        'generate_video': generate_video
    }


def create_content_agent(region):
    """Create the content generator agent."""
    # Disable tool consent prompts for automation
    os.environ['BYPASS_TOOL_CONSENT'] = 'true'
    
    # Create Bedrock model with session region
    session = boto3.Session(region_name=region)
    model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        boto_session=session
    )
    
    # Create content generator agent
    agent = Agent(
        model=model,
        tools=[
            generate_image,
            nova_reels,
            use_aws,
            file_write
        ],
        system_prompt="""You are a professional travel content creator that generates complete content packages.

Your tools:
- generate_image: Create high-quality destination images with Amazon Nova Canvas (saves PNG locally)
- nova_reels: Generate promotional videos with Amazon Nova Reel (saves to S3)
- use_aws: Download files from S3 or perform other AWS operations
- file_write: Create text files for itineraries

When the user provides a destination, you MUST:

1. **Generate Destination Image**:
   - Use generate_image tool
   - Create a stunning photo of the main landmark at golden hour
   - Include detailed prompt with: lighting, composition, atmosphere, mood
   - Professional travel photography quality
   - The tool will save the PNG file automatically

2. **Generate Tour Video** (if S3 bucket provided):
   - First, use nova_reels tool with action="create"
   - Create a 6-second cinematic tour
   - CRITICAL: Text prompt MUST be under 512 characters
   - Show 3-4 iconic locations with smooth camera movement
   - Pass text, s3_bucket parameters
   - Save the invocation_arn from the response
   - IMPORTANT: Video generation takes 5-10 minutes
   - Keep checking status with nova_reels action="status" repeatedly
   - Continue checking until status is "Completed" (not "InProgress")
   - Only when status is "Completed", extract the S3 output URI from the response
   - Parse the S3 URI to get bucket and key
   - Then use use_aws to download the video:
     * service_name: "s3"
     * operation_name: "download_file"
     * parameters: {"Bucket": bucket_name, "Key": video_key, "Filename": "output/[destination]-tour.mp4"}
   - DO NOT attempt download until status is "Completed" WAIT for the status Completed, alwayls wait.

3. **Create Travel Itinerary**:
   - Use file_write tool
   - Generate detailed day-by-day itinerary as text
   - Include: activities, restaurants, cultural insights, transportation tips
   - Match the travel style and season provided
   - Save to output/[destination]-itinerary.txt
   - Format with clear sections: Day 1, Day 2, etc.

Guidelines:
- Be creative and professional
- Use specific location names and landmarks
- Include atmospheric details
- Ensure video prompts are concise (under 512 chars)
- For video generation, wait for completion before downloading
- Generate ALL pieces of content automatically

Always execute all available tools when given a destination.
"""
    )
    
    return agent


def generate_content(config):
    """Generate travel content based on configuration."""
    # Get AWS region from session
    session = boto3.Session()
    region = session.region_name or 'us-east-1'
    
    print(f"\n🌐 Using AWS region: {region}")
    
    # Create agent
    print("🤖 Creating content generator agent...")
    agent = create_content_agent(region)
    
    # Extract city from destination
    city = config['destination'].split(',')[0].strip()
    country = config['destination'].split(',')[1].strip() if ',' in config['destination'] else ""
    
    # Check if video generation is possible
    skip_video = not config['generate_video'] or not config['bucket']
    video_instruction = "Skip video generation (disabled or no S3 bucket configured)." if skip_video else f"Generate video using S3 bucket: {config['bucket']}"
    
    print("\n" + "="*80)
    print("🎨 Generating Content...")
    print("="*80)
    print(f"📍 Destination: {config['destination']}")
    print(f"🏛️  Landmark: {config['landmark']}")
    print(f"📅 Duration: {config['duration']} days")
    print(f"🎨 Style: {config['style']}")
    print(f"🌤️  Season: {config['season']}")
    if config['generate_video']:
        print(f"🎬 Video: Yes (bucket: {config['bucket']})")
    else:
        print("🎬 Video: No")
    print("="*80 + "\n")
    
    # Generate content
    prompt = f"""
Generate a complete travel content package for:

Destination: {config['destination']}
City: {city}
Country: {country}
Main Landmark: {config['landmark']}
Trip Duration: {config['duration']} days
Travel Style: {config['style']}
Season: {config['season']}

Video generation: {video_instruction}
{'S3 Bucket: ' + config['bucket'] if not skip_video else ''}

Create {'image and itinerary' if skip_video else 'all three pieces of content (image, video, and itinerary)'}.
Use the exact parameters provided above.

For video generation:
1. Use nova_reels to create the video (it will be saved to S3)
2. IMPORTANT: Keep checking status repeatedly until it shows "Completed" (takes 5-10 minutes)
3. Only after status is "Completed", use use_aws to download the video from S3 to output/
4. Do NOT skip the waiting period - the video must be fully generated before download
"""
    
    response = agent(prompt)
    
    print("\n" + "="*80)
    print("✅ Content Generation Complete")
    print("="*80)
    print(response)
    print()


def verify_content():
    """Verify generated content."""
    from pathlib import Path
    
    output_dir = Path("output")
    
    print("\n" + "="*80)
    print("📁 Generated Content")
    print("="*80)
    
    if output_dir.exists():
        # Images
        images = list(output_dir.glob("*.jpg")) + list(output_dir.glob("*.png"))
        if images:
            print("\n🖼️  Images:")
            for img in images:
                size_mb = img.stat().st_size / (1024 * 1024)
                print(f"  • {img.name} ({size_mb:.2f} MB)")
        
        # Videos
        videos = list(output_dir.glob("*.mp4"))
        if videos:
            print("\n🎬 Videos:")
            for vid in videos:
                size_mb = vid.stat().st_size / (1024 * 1024)
                print(f"  • {vid.name} ({size_mb:.2f} MB)")
        
        # Itineraries
        itineraries = list(output_dir.glob("*.txt"))
        if itineraries:
            print("\n📄 Itineraries:")
            for txt in itineraries:
                size_kb = txt.stat().st_size / 1024
                print(f"  • {txt.name} ({size_kb:.2f} KB)")
        
        total_files = len(list(output_dir.glob("*")))
        print(f"\n✅ Total files: {total_files}")
    else:
        print("\n❌ No content directory found")
    
    print("="*80 + "\n")


def main():
    """Main application entry point."""
    try:
        # Get user input
        config = get_user_input()
        
        # Generate content
        generate_content(config)
        
        # Verify generated content
        verify_content()
        
        print("🎉 All done! Your travel content is ready.\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
