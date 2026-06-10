print("🔥 [DEBUG] STARTING THE FAST-RENDER VIDEO FACTORY WORKER...")
import sqlite3, time, json, os
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

try:
    from moviepy.video.fx import concatenate_videoclips
except ImportError:
    try:
        from moviepy import concatenate_videoclips
    except ImportError:
        from moviepy.video.compositing.util import concatenate_videoclips

DB_PATH = '/home/djallel/ai_video_factory/factory.db'
OUTPUT_DIR = '/home/djallel/ai_video_factory/output_videos'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_premium_background(text, output_path, index):
    width, height = 1920, 1080
    gradients = [
        ((15, 32, 67), (32, 124, 229)),
        ((24, 18, 43), (91, 50, 125)),
        ((10, 35, 36), (41, 120, 90))
    ]
    color_top, color_bottom = gradients[index % len(gradients)]
    base = Image.new('RGB', (width, height), color_top)
    top_factor = Image.new('RGB', (width, height), color_bottom)
    mask = Image.new('L', (width, height))
    mask_data = [int(255 * (y / height)) for y in range(height) for x in range(width)]
    mask.putdata(mask_data)
    img = Image.composite(top_factor, base, mask)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
    except:
        font = ImageFont.load_default()

    words = text.split()
    lines, current_line = [], []
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > 50:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    
    draw.rectangle([0, height - 250, width, height], fill=(0, 0, 0, 160))
    y_text = height - 190
    for line in lines:
        text_w = draw.textlength(line, font=font)
        draw.text(((width - text_w) // 2, y_text), line, fill=(255, 255, 255), font=font)
        y_text += 60
    img.save(output_path)

def process_video_job(job_id, title, script_text):
    print(f"\n🎬 [Massive Factory] RENDER IN PROGRESS: '{title}'")
    temp_clips = []
    try:
        script = json.loads(script_text)
        for index, line in enumerate(script):
            text = line['text']
            audio_path = f"/tmp/audio_{index}.mp3"
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(audio_path)
            
            image_path = f"/tmp/image_{index}.png"
            create_premium_background(text, image_path, index)
            
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.5
            
            # كود مستقر ومباشر بدون عمليات تعديل أطر معقدة تسبب التهنيج
            video_clip = ImageClip(image_path).with_duration(duration)
            video_clip = video_clip.with_audio(audio_clip)
            temp_clips.append(video_clip)
            
        final_video = concatenate_videoclips(temp_clips, method="compose")
        final_output_path = os.path.join(OUTPUT_DIR, f"{title.replace(' ', '_').lower()}_{job_id[:8]}.mp4")
        
        print(f"💾 Writing final production file to disk...")
        
        # رندرة قياسية فائقة التوافق والاستقرار
        final_video.write_videofile(
            final_output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac"
        )
        
        for clip in temp_clips: clip.close()
        final_video.close()
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE jobs SET status='completed' WHERE id=?", (job_id,))
        conn.commit()
        conn.close()
        print(f"🏆 [PRO PROFIT READY] Video '{title}' is beautifully rendered at {final_output_path}!\n")
    except Exception as e:
        print(f"❌ Error in production: {e}")

# تنظيف الحالات العالقة لتشغيلها من جديد
try:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE jobs SET status='pending' WHERE status='processing'")
    conn.commit()
    conn.close()
except:
    pass

while True:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, script_text FROM jobs WHERE status='pending' LIMIT 1")
        job = cursor.fetchone()
        if job:
            job_id, title, script_text = job
            cursor.execute("UPDATE jobs SET status='processing' WHERE id=?", (job_id,))
            conn.commit()
            conn.close()
            process_video_job(job_id, title, script_text)
        else:
            print("👁️ Looking for pending video scripts...")
            conn.close()
    except Exception as e:
        print(f"❌ [DB Error]: {e}")
    time.sleep(3)
