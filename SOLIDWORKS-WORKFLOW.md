# SolidWorks + Git workflow

## Adding a project
1. In SolidWorks, open the top-level assembly and run **File > Pack and Go**.
   - Check **Include drawings** (and simulation results only if you want them).
   - Choose **Flatten to single folder** and save to `projects/<name>/cad/`.
   - Pack and Go collects every referenced part, so the assembly opens with no missing files.
2. Make exports into `exports/`:
   - **STEP AP214** (`File > Save As > STEP`) for anyone with other CAD tools.
   - **eDrawings** (`.easm` / `.eprt`) so people can rotate the model in the free viewer.
   - **STL** for 3D-printed parts. GitHub shows `.stl` files as interactive 3D previews.
3. Save drawings as **PDF** into `drawings/`.
4. Take renders or screenshots (Visualize, PhotoView 360, or `View > Save as image`) into `renders/`.
5. Commit and push:
   ```
   git add .
   git commit -m "Add <project name>"
   git push
   ```

## Rules of thumb
- **Close SolidWorks before committing.** Open files leave `~$` lock files and may not be fully saved.
- **Don't rename or move files in Windows Explorer.** Use SolidWorks Explorer or Pack and Go, or the assembly will lose its references.
- **Toolbox parts** (bolts, nuts): set Toolbox to "make parts" copies or include them in Pack and Go, or they show as missing on other computers.
- **Version:** note which SolidWorks version you saved in. Older versions can't open newer files, and student and commercial licenses can differ.
- **Student license watermark:** files saved with an educational license are marked as such when opened in commercial SolidWorks. That's fine for a portfolio, but mention it if an employer asks for native files.
- **Commit at milestones** (design review, revision, final), with messages like `Rev B: thickened bracket web after FEA`. Git history then becomes your revision log.
