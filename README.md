# SHRINK: Data Compression by Semantic Extraction and Residuals Encoding
Welcome to the repository accompanying our IEEE BIG DATA 2024 paper [SHRINK: Data Compression by Semantic Extraction and Residuals Encoding
](https://arxiv.org/abs/2410.06713). We propose a new type of compression algorithm called SHRNK that produces a high efficient encoding for time series data using PLA technique.


## Dataset files
Download from the following Google Drive link: https://drive.google.com/drive/folders/1gxU9GskX9f60meHUnwcaqs0FvE75tuEN?usp=sharing

## Requirements:
- Create a new Python virtual environment 
- Install the dependencies via `pip install -r requirements.txt`
- We used TRC as our downstream compression as explained in the paper. It can be installed through the link: https://github.com/powturbo/Turbo-Range-Coder
- Compile for TRC:<br>
        Download or clone TurboRC<br>
	git clone --recursive https://github.com/powturbo/Turbo-Range-Coder.git<br>
        cd Turbo-Range-Coder<br>
        make<br>

## Our method: HIRE
- Located in `hier.py`
- `HierarchicalSketch` class implements univariate HIRE
- `MultivariateHierarchical` class implements multivariate HIRE

Detailed comments explaining the correspondence beteween parts of the code and the paper can be found throughout.  
## Main experiment file
1) Navigate to `experiments.py` and choose baselines you would like to run in `initialize(...)`
2) Change data path to the dataset location in `run(..., DATA_DIRECTORY = "your_path", FILENAME = "data_file")`
3) Change results path for desired metrics in the `with open(...)` statements
4) Run file

## LFZip, Buff, and optimal split experiments
- `cd revision_HIRE_experiments/`
- Place the datasets in the `datasets/` directory (from the below Google Drive link)
1) To run LFZip, create a conda virtual environment and `conda install lfzip`. Then run `python3 experiments_LFZip.py`
2) To run Buff, first install the rust programming language on your local machine: https://www.rust-lang.org/tools/install. Then `cd buff-master/database` and `python3 buff_experiments.py`
3) To run the optimal splitting experiment `python3 optimal_splitting_experiments.py` For the ablation study of the optimal split, run `python3 optimal_splitting_experiments_ablation.py`
4) To run the experiments comparing the different error functions at various levels of the hierarchy, run `python3 experiments_other_errs.py`

# Citation
If you use SHRINK in your paper, please use the following citation:

`@inproceedings{sun2024shrink,
  title={SHRINK: Data Compression by Semantic Extraction and Residuals Encoding},
  author={Sun, Guoyou and Karras, Panagiotis and Zhang, Qi},
  booktitle={2024 IEEE International Conference on Big Data (BigData)},
  pages={650--659},
  year={2024},
  organization={IEEE}
}`

