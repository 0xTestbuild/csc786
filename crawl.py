import os

output_file = "project_dump.txt"
root_folder = "./"

with open(output_file, "w", encoding="utf8") as out:
    for folder, subfolders, files in os.walk(root_folder):
        for name in files:
            path = os.path.join(folder, name)
            try:
                with open(path, "r", encoding="utf8") as f:
                    out.write(f"FILE START: {path}\n")
                    out.write(f.read())
                    out.write("\n\nFILE END\n\n")
            except Exception as e:
                out.write(f"FILE START: {path}\n")
                out.write("Could not read this file.\n\nFILE END\n\n")

print("Finished gathering files.")
