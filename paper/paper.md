---
title: 'FastGeodis: Fast Generalised Geodesic Distance Transform'
tags:
  - Python
  - PyTorch
  - Deep Learning
  - Medical Imaging
  - Distance Transform
authors:
  - name: Muhammad Asad
    orcid: 0000-0002-3672-2414
    affiliation: 1
    corresponding: true
  - name: Reuben Dorent
    orcid: 0000-0002-7530-0644
    affiliation: 1
  - name: Tom Vercauteren
    orcid: 0000-0003-1794-0456
    affiliation: 1
affiliations:
 - name: School of Biomedical Engineering & Imaging Sciences, King’s College London, UK
   index: 1
date: 23 June 2022
bibliography: paper.bib
---

# Summary 

  
Geodesic and Euclidean distance transforms have been widely used in a number of applications where distance from a set of reference points is computed. Methods from recent years have shown effectiveness in applying Geodesic distance transform to interactively annotate 3D medical imaging data [@wang2018deepigeos; @criminisi2008geos]. The Geodesic distance transform enables providing segmentation labels, i.e., voxel-wise labels, for different objects of interests. Despite existing methods for efficient computation of the Geodesic distance transform on GPU and CPU devices [@criminisiinteractive; @criminisi2008geos; @weber2008parallel; @toivanen1996new], an open-source implementation of such methods on the GPU does not exist. 
On the contrary, efficient methods for the computation of the Euclidean distance transform [@felzenszwalb2012distance] have open-source implementations [@tensorflow2015-whitepaper; @eucildeantdimpl]. Existing libraries, e.g., [@geodistk], provide C++ implementations of the Geodesic distance transform, however they lack efficient utilisation of the underlying hardware and hence result in significant computation time especially when applying them on 3D medical imaging volumes.  

The `FastGeodis` package provides an efficient implementation for computing Geodesic and Euclidean distance transforms (or a mixture of both) targeting efficient utilisation of CPU and GPU hardwares. In particular, it implements paralellisable raster scan method from [@criminisiinteractive], where elements in row (2D) or plane (3D) can be computed with parallel threads. This package is able to handle 2D as well as 3D data where it achieves up to 20x speed-up on CPU and up to 74x speed-up on GPU as compared to an existing open-source library [@geodistk] which uses non-parallelisable single-thread CPU implementation. The performance speed-ups reported here were evaluated using 3D volume data on Nvidia GeForce Titan X (12 GB) with 6-Core Intel Xeon E5-1650 CPU. Further in-depth comparison of performance improvements is discussed in `FastGeodis` \href{https://masad.ml/FastGeodis/}{documentation}. 

# Statement of need 
 
Despite existing open-source implementation of distance transforms [@tensorflow2015-whitepaper; @eucildeantdimpl; @geodistk], open-source implementations of efficient Geodesic distance transform algorithms [@criminisiinteractive; @weber2008parallel] on CPU and GPU do not exist. However, efficient CPU [@eucildeantdimpl] and GPU [@tensorflow2015-whitepaper] implementations exist for Euclidean distance transform. To the best of our knowledge, `FastGeodis` is the first open-source implementation of efficient Geodesic distance transform [@criminisiinteractive], achieving up to 20x speed-up on CPU and up to 74x speed-up on GPU as compared to existing open-source libraries [@geodistk]. It also provides efficient implementation of Euclidean distance transform. In addition, it is the first open-source implementation of generalised Geodesic distance transform and Geodesic Symmetric Filtering (GSF) proposed in [@criminisi2008geos]. Apart from method from [@criminisiinteractive], [@weber2008parallel] presents a further optimised approach for computing Geodesic distance transforms on GPUs, however this method is protected by multiple patents and hence is not suitable for open-source implementation in **FastGeodis** package.
  

The ability to efficiently compute Geodesic and Euclidean distance transforms can significantly enhance distance transform applications especially for training deep learning models that utilise distance transforms [@wang2018deepigeos]. It will improve prototyping, experimentation, and deployment of such methods, where efficient computation of distance transforms has been a limiting factor. In 3D medical imaging problems, efficient computation of distance transforms will lead to significant speed-ups, enabling online learning applications for better processing/labelling/inference from volumetric datasets [@asad2022econet].  In addition, `FastGeodis` provides efficient implementation for both CPUs and GPUs hardware and hence will enable efficient use of a wide range of hardware devices. 

  
# Implementation 


`FastGeodis` implements an efficient distance transform algorithm from [@criminisiinteractive], which provides parallelisable raster scans to compute distance transform. The implementation consists of data propagation passes parallelised using threads for elements across a line (2D) or plane (3D). \autoref{fig:hwpasses} shows these data propagation passes, where each pass consists of computing distance values for next row (2D) or plane (3D) by utilising parallel threads and data from previous row/plane, hence resulting in propagating distance values along the direction of pass. For 2D data, four distance propagation passes are required, top-bottom, bottom-top, left-right and right-left, whereas for 3D data six passes are required, front-back, back-front, top-bottom, bottom-top, left-right and right-left. The algorithm can be applied to efficiently compute both Geodesic and Euclidean distance transforms. In addition to this, `FastGeodis` also provides non-parallelisable raster scan based distance transform method from [@toivanen1996new], which is implemented using single-thread CPU and used for comparison.


`FastGeodis` package is implemented using `PyTorch` [@NEURIPS2019_9015] utilising OpenMP for CPU and CUDA for GPU parallelisation of the algorithm. It is accessible as a python package, that can be installed across different operating systems and devices. Comprehensive documentation and a range of examples are provided for understanding the usage of the package on 2D and 3D data using CPU or GPU. Two- and three-dimensional examples are provided for Geodesic, Euclidean, Signed Geodesic distance transform as well as computing Geodesic Symmetric Filtering (GSF), the essential first step in implementing interactive segmentation method described in [@criminisi2008geos]. Further in-depth overview of implemented algorithm, along with evaluation on common 2D/3D data input sizes is provided in `FastGeodis` \href{https://masad.ml/FastGeodis/}{documentation}.

  

![Raster scan data propagation passes in FastGeodis.\label{fig:hwpasses}](FastGeodis.png){ width=80% } 

# Acknowledgements

This research was supported by the European Union’s Horizon 2020 research and innovation programme under grant agreement No 101016131. 

# References
