#@ File    (label = "Input directory", style = "directory") srcFile
#@ File    (label = "8-bit Output directory", style = "directory") bit8Dir
#@ File    (label = "Label Output directory", style = "directory") labelDir
#@ String  (label = "File extension", value=".tif") ext

#@ DatasetIOService io
#@ CommandService command
#@ UIService ui # for interactive debugging of label image segmentation with ui.show() calls

from ij import IJ, WindowManager
from ij.plugin.frame import RoiManager
from de.csbdresden.stardist import StarDist2D

from glob import glob
import os

# Fetch the absolute paths of the source and 8-bit output directories
srcDir = srcFile.getAbsolutePath()
bit8Dir = bit8Dir.getAbsolutePath()
labelDir = labelDir.getAbsolutePath()

# Function to get the filename without the path
def get_filename(file_path):
    return os.path.basename(file_path)

# Function to convert images to 8-bit and save them
def convert_to_8bit(inputDir, outputDir, prefix=""):
    for f in sorted(glob(os.path.join(inputDir, "*" + ext))):
        print("Converting to 8-bit: " + get_filename(f))

        # Open the image
        imp = IJ.openImage(f)
        
        # Minimize artifacts from microscopy lighting and set a global scale for accurate processing
        # Only applied to images in the source directory
        if inputDir == srcDir:
            IJ.run(imp, "Subtract Background...", "rolling=10")
            IJ.run(imp, "Set Scale...", "distance=1.075 known=1 unit=µm global")

        # Convert to 8-bit image and save
        IJ.run(imp, "8-bit", "")
        IJ.save(imp, os.path.join(outputDir, prefix + get_filename(f)))

# Function to run StarDist on all 8-bit TIF files in the specified directory
def batch_process_StarDist():
    # Open the ROI Manager
    rm = RoiManager.getRoiManager()
    if rm is None:
        rm = RoiManager()
    
    # Open or create the .dat file for saving the results
    output_file_path = os.path.join(labelDir, "cell_counts.dat")
    with open(output_file_path, "w") as output_file:
        for f in sorted(glob(os.path.join(bit8Dir, "*" + ext))):
            print("Processing: " + get_filename(f))

            # Open the image
            imp = IJ.openImage(f)

            # Run StarDist2D
            res = command.run(StarDist2D, False,
                              "input", imp,
                              "modelChoice", "Versatile (fluorescent nuclei)",
                              "outputType", "Both").get()

            # Retrieve the label image and save
            label = res.getOutput("label")
            #ui.show(label)
            io.save(label, os.path.join(labelDir, "label_" + get_filename(f)))

            # Count the number of ROIs (cells) and write the counts to a .dat file
            if rm is not None:
                n_cells = rm.getCount()
                output_file.write(get_filename(f) + ": " + str(n_cells) + "\n")

                # Optionally, clear the ROI Manager for the next image
                rm.reset()

# Execute the conversion and batch processing
convert_to_8bit(srcDir, bit8Dir, prefix="8bit_")
batch_process_StarDist()
convert_to_8bit(labelDir, labelDir)

# Close the ROI Manager window at the end of the batch processing
if WindowManager.getFrame("ROI Manager") is not None:
    WindowManager.getFrame("ROI Manager").close()