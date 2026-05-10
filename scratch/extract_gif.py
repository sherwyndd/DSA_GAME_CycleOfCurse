from PIL import Image
import os

def extract_gif_frames():
    gif_path = r'C:\Users\HP\Documents\DSA-Game-Project\UkM03M-ezgif.com-crop.gif'
    target_dir = r'c:\Users\HP\Documents\DSA-Game-Project\graphics\particles\frost'
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")

    try:
        with Image.open(gif_path) as im:
            # We want 4 frames. If there are more, we can sample them.
            # If there are fewer, we take what we have.
            num_frames = im.n_frames
            print(f"Total frames in GIF: {num_frames}")
            
            # Step size to get 4 frames
            step = max(1, num_frames // 4)
            
            for i in range(4):
                frame_idx = i * step
                if frame_idx >= num_frames:
                    frame_idx = num_frames - 1
                
                im.seek(frame_idx)
                # Convert to RGBA
                frame = im.convert('RGBA')
                
                # Make black background transparent if needed
                datas = frame.getdata()
                new_data = []
                for item in datas:
                    # If it's pure black or very close, make it transparent
                    if item[0] < 10 and item[1] < 10 and item[2] < 10:
                        new_data.append((0, 0, 0, 0))
                    else:
                        new_data.append(item)
                frame.putdata(new_data)
                
                save_path = os.path.join(target_dir, f'{i}.png')
                frame.save(save_path)
                print(f"Saved frame {frame_idx} as {save_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_gif_frames()
