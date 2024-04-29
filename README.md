# Downloads:

1.	Download Fiji (ImageJ) from: https://downloads.imagej.net/fiji/archive/20230710-2317/ <br />
            - Do not update beyond this version! You should be running v1.54f. <br />
  	  - v1.54i (the 03/2024 update) is buggy and not yet fully headless compatible. <br />
  	  - If you are having trouble downloading the older version, let me know and I will email you a zip file of the installation.

3.	Download StarDist, following the instructions from this link exactly: https://imagej.net/plugins/stardist#installation

4.	Check this link for more info on the plugin and what each parameter means: https://imagej.net/plugins/stardist#usage


# Usage:

python StarDist_cmd.py "path\to\ImageJ.exe" "path\to\unprocessed\images"
                       "path\to\preprocessing\script" "path\to\preprocessed\images"
                       "model_folder_or_pretrained_name" "path\to\postprocessed\images" -v
