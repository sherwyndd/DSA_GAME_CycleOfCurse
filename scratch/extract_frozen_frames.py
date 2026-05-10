from PIL import Image
import os

def extract_frozen_frames():
    """Extract up to four frames from the specified GIF and save them as PNGs.
    The frames are saved into the 'graphics/particles/frozen' directory.
    """
    gif_path = r'C:\Users\HP\Documents\DSA-Game-Project\UkM03M-ezgif.com-crop.gif'
    target_dir = r'C:\Users\HP\Documents\DSA-Game-Project\graphics\particles\frozen'

    # Ensure target directory exists
    os.makedirs(target_dir, exist_ok=True)
    print(f"Target directory: {target_dir}")

    try:
        with Image.open(gif_path) as im:
            num_frames = getattr(im, 'n_frames', 1)
            print(f"Total frames in GIF: {num_frames}")
            # Determine step to sample roughly 4 frames
            step = max(1, num_frames // 4)
            for i in range(4):
                frame_idx = i * step
                if frame_idx >= num_frames:
                    frame_idx = num_frames - 1
                im.seek(frame_idx)
                frame = im.convert('RGBA')
                # Make near‑black pixels transparent (optional)
                datas = frame.getdata()
                new_data = []
                for item in datas:
                    if item[0] < 10 and item[1] < 10 and item[2] < 10:
                        new_data.append((0, 0, 0, 0))
                    else:
                        new_data.append(item)
                frame.putdata(new_data)
                save_path = os.path.join(target_dir, f"{i}.png")
                frame.save(save_path)
                print(f"Saved frame {frame_idx} as {save_path}")
    except Exception as e:
        print(f"Error extracting frames: {e}")

if __name__ == "__main__":
    extract_frozen_frames()
