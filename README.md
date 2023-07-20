
# EDArtifact 
EDArtifact is a repository that contains three main items as following:

- *EDArtifact_Dashboard*: is a dashboard used to **manually** label artifacts in electrodermal activity (EDA) data. The dashboard has been implemented to easily inspect and label EDA signals collected in the wild over long periods of time i.e., several hours or days. The folder contains detailed instructions on how to install and use the dashboard.
- *EDArtifacts_Detection*: contains the scripts and the model for **automatic** identification of artifacts in EDA signals. The folder includes instructions on how to run the scripts for identifying artifacts in your data. 
- *EDArtifacts_Guidelines*: contains the guidelines for manual labeling of artifacts in EDA signals.

If you use the scripts for automatic identification of artifacts or the guidelines and the dashboard for manual labeling of atifacts in EDA signals, please cite the paper [1]: 

[1] S. Gashi, E. Di Lascio, B. Stancu, V. Das Swain, V. Mishra, M. Gjoreski, S. Santini: "Detection of Artifacts in Ambulatory Electrodermal Activity Data". In:  Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies (PACM IMWUT), Vol. 4, Issue 2, June 2020. 31 pages. 

The paper is available at https://dl.acm.org/doi/10.1145/3397316. 

Please do not hesitate to contact us at silvia.santini@usi.ch if you have any questions in general or experience issues with the tools.

-----
This package was made pip-installable by @LeonardoAlchieri: feel free to contact him as well. While all requirements should be installed using pip, one of them is not available through pypi at the moment: you can just install it using:
```bash
pip install git+https://github.com/LeonardoAlchieri/cvxEDA.git
```
Otherwise, you can create a new conda (or even better, [mamba](https://github.com/mamba-org/mamba)) running the following command:
```bash
conda create -f env.yml
```
or (*even better!*)
```bash
mamba create -f env.yml
```









