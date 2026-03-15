# Semantic Road Marking Understanding

## Lane Detection → Structured Representation Pipeline (CULane Demo)

### Project Overview
This project is a research prototype for transforming lane detection outputs into structured semantic representations that can later be used for LLM-based traffic reasoning.  
Current stage includes:
1. Loading CULane dataset  
2. Parsing `.lines.txt` lane annotations  
3. Visualizing detected lanes / showing simple LLM indication  
4. Basic lane classification (left/right based on image center)  

---

### Dataset
[CULane Dataset on Kaggle](https://www.kaggle.com/datasets/greatgamedota/culane)

Dataset structure:
```text
culane_root/ 
│   
|__ driver_161_90frame/ 
│  |__ 06030819_0755.MP4/ 
│  │  |__ 0000.jpg 
│  │  |__ 0000.lines 
│  │  |__ 0001.jpg 
│  │  |__ 0001.lines 
│  |__ ... 
│__ driver_161_90frame_labels/ 
|  |__ 06030819_0755.MP4/ 
│  |__ 0000.png 
│  |__ ...
```
---

### Project Structure
```text
semantic-road-marking-understanding/
|__
│  |__ src/ 
│  |  |__ dataset.py          # CULane dataset loader 
│  |  |__ visualize.py        # Lane visualization utilities 
│  |  |__ lane_processing.py  # Lane classification logic 
│  |  |__ main.py             # Entry point 
│  |  |__ llm_interface.py    # LLM interface 
│  |  |__ ... 
│  |__ README.md
```
---

### Installation & Run
1. **Install dependencies:**
   ```bash
   pip install opencv-python numpy
   python download_dataset.py
   python main.py
