#@ File    (label = "Input directory", style = "directory") srcFile
#@ File    (label = "8-bit Output directory", style = "directory") bit8Dir
#@ File    (label = "Label Output directory", style = "directory") labelDir
#@ String  (label = "File extension", value=".tif") ext

#@ DatasetIOService io
#@ CommandService command
#@ UIService ui  # for interactive debugging of label image segmentation with ui.show() calls

from ij import IJ, WindowManager
from ij.plugin.frame import RoiManager
from de.csbdresden.stardist import StarDist2D

from glob import glob
import os

# Initialize logging
log_file_path = os.path.join(labelDir.getAbsolutePath(), "proc_log.txt")
log_file = open(log_file_path, "w")

def log(message):
    #print(message)  # Show message in the console
    log_file.write(message + "\n")  # Write message to log file

# Function to display progress bar
def show_progress(current, total):
    pct = (current / float(total)) * 100
    print("Progress: {:.2f}%".format(pct))

# Function to get the filename without the path
def get_filename(file_path):
    return os.path.basename(file_path)

# Function to convert images to 8-bit and save them
def convert_to_8bit(inputDir, outputDir, srcDir, ext, prefix=""):
    log("\n--- Converting to 8-bit ---")
    files = sorted(glob(os.path.join(inputDir, "*" + ext)))
    for idx, f in enumerate(files):
        log("Converting to 8-bit: {}".format(get_filename(f)))
        
        # Open the image
        imp = IJ.openImage(f)

        # Minimize artifacts from microscopy lighting and set a global scale for accurate processing
        if inputDir == srcDir:
            IJ.run(imp, "Subtract Background...", "rolling=10")
            IJ.run(imp, "Set Scale...", "distance=1.075 known=1 unit=µm global")

        # Convert to 8-bit image and save
        IJ.run(imp, "8-bit", "")
        IJ.save(imp, os.path.join(outputDir, prefix + get_filename(f)))

# Function to run StarDist on all 8-bit TIF files in the specified directory
def batch_process_StarDist(bit8Dir, labelDir, ext, command):
    log("\n--- Running StarDist ---")
    rm = RoiManager.getRoiManager()
    if rm is None:
        rm = RoiManager()

    output_file_path = os.path.join(labelDir, "cell_counts.dat")
    with open(output_file_path, "w") as output_file:
        files = sorted(glob(os.path.join(bit8Dir, "*" + ext)))
        for idx, f in enumerate(files):
            label_output_path = os.path.join(labelDir, "label_" + get_filename(f))
            if os.path.exists(label_output_path):
                log("Skipping {}, already processed.".format(get_filename(f)))
                continue
            
            log("Processing: {}".format(get_filename(f)))
            show_progress(idx + 1, len(files))

            imp = IJ.openImage(f)
            res = command.run(
            				  StarDist2D, False,
                              "input", imp,
                              "modelChoice", "Versatile (fluorescent nuclei)",
                              "outputType", "Both",
                              "normalizeInput", True,  # default
                              "percentileBottom", 1.0,  # default
                              "percentileTop", 99.8,  # default
                              "probThresh", 0.5,  # default
                              "nmsThresh", 0.4  # default
                             ).get()

            label = res.getOutput("label")
            io.save(label, label_output_path)

            if rm is not None:
                n_cells = rm.getCount()
                output_file.write("{}: {}\n".format(get_filename(f), str(n_cells)))
                rm.reset()

if __name__ == "__main__":
    srcDir = srcFile.getAbsolutePath()
    bit8Dir = bit8Dir.getAbsolutePath()
    labelDir = labelDir.getAbsolutePath()

    convert_to_8bit(srcDir, bit8Dir, srcDir, ext, prefix="8bit_")
    batch_process_StarDist(bit8Dir, labelDir, ext, command)
    convert_to_8bit(labelDir, labelDir, srcDir, ext)
    
    WindowManager.getFrame("ROI Manager").close()

    log_file.close()
