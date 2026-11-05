add app file
import os
import uuid
import shutil
import traceback
import gradio as gr
from gradio_client import Client, handle_file

# AI Video Server
SPACE_ID = "Lightricks/ltx-video-distilled"

print("Connecting to AI server...")

client = Client(SPACE_ID)

print("AI server connected!")

def generate_video(mode, prompt, image, duration):

    if not prompt or not prompt.strip():
        return None, "Please enter a video prompt!"

    if mode == "Image to Video" and image is None:
        return None, "Please upload an image first!"

    try:
        if mode == "Text to Video":
            api_name = "/text_to_video"
            image_input = None
            model_mode = "text-to-video"

        else:
            api_name = "/image_to_video"
            image_input = handle_file(image)
            model_mode = "image-to-video"

        result = client.predict(
            prompt,
            "worst quality, blurry, distorted, jittery",
            image_input,
            None,
            512,
            704,
            model_mode,
            float(duration),
            9,
            42,
            True,
            1.0,
            True,
            api_name=api_name
        )

        generated = result[0]

        if isinstance(generated, dict):
            video_path = (
                generated.get("video")
                or generated.get("path")
            )
        else:
            video_path = generated

        if not video_path:
            raise Exception("AI server did not return a video.")

        if not os.path.exists(video_path):
            raise Exception("Generated video file not found.")

        os.makedirs("generated_videos", exist_ok=True)

        filename = os.path.join(
            "generated_videos",
            "video_" + uuid.uuid4().hex[:8] + ".mp4"
        )

        shutil.copy2(video_path, filename)

        return filename, "Video generated successfully!"

    except Exception as e:
        traceback.print_exc()
        return None, "Error: " + str(e)


# AI VIDEO STUDIO
with gr.Blocks(
    theme=gr.themes.Soft(),
    title="Sudais AI Video Studio"
) as demo:

    gr.Markdown("""
    # 🎬 SUDAIS AI VIDEO STUDIO

    ### Create Amazing AI Videos

    Turn your imagination and photos into videos!
    """)

    with gr.Row():

        with gr.Column():

            mode = gr.Radio(
                ["Text to Video", "Image to Video"],
                value="Text to Video",
                label="Select Generation Mode"
            )

            prompt = gr.Textbox(
                label="Video Prompt",
                placeholder="A beautiful sunset over mountains...",
                lines=4
            )

            image = gr.Image(
                label="Upload Your Photo",
                type="filepath"
            )

            duration = gr.Slider(
                minimum=2,
                maximum=8,
                value=2,
                step=1,
                label="Video Duration (seconds)"
            )

            generate = gr.Button(
                "✨ Generate AI Video",
                variant="primary"
            )

        with gr.Column():

            output = gr.Video(
                label="Your AI Generated Video"
            )

            status = gr.Textbox(
                label="Generation Status"
            )

    generate.click(
        fn=generate_video,
        inputs=[mode, prompt, image, duration],
        outputs=[output, status]
    )

    gr.Markdown("""
    ---
    **Powered by LTX Video AI**

    Text to Video | Image to Video | MP4 Output
    """)


# Render Server
port = int(os.environ.get("PORT", 7860))

demo.queue().launch(
    server_name="0.0.0.0",
    server_port=port
)
