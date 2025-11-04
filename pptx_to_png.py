import os
import comtypes.client

def pptx_to_png(pptx_path, output_folder):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Create PowerPoint Application object
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1
    
    # Open the presentation
    presentation = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
    
    # Export each slide as PNG
    presentation.Export(output_folder, "PNG")
    
    # Close and quit
    presentation.Close()
    powerpoint.Quit()
    
    print(f"✅ Slides exported as PNG images in: {output_folder}")

if __name__ == "__main__":
    pptx_file = r"D:\pptx\Pop-ups_FEMB_QC.pptx"
    output_dir = r"D:\pptx\pngs"
    pptx_to_png(pptx_file, output_dir)

