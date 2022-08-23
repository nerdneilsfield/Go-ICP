/********************************************************************
Main Function for point cloud registration with Go-ICP Algorithm
Last modified: Feb 13, 2014

"Go-ICP: Solving 3D Registration Efficiently and Globally Optimally"
Jiaolong Yang, Hongdong Li, Yunde Jia
International Conference on Computer Vision (ICCV), 2013

Copyright (C) 2013 Jiaolong Yang (BIT and ANU)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*********************************************************************/

#include <chrono>
#include <fstream>
#include <iostream>
// #include <thread>
// #include <time.h>
using namespace std;

#include "ConfigMap.hpp"
#include "jly_goicp.h"

#include "simple_timer.hpp"
#define DEFAULT_OUTPUT_FNAME "output.txt"
#define DEFAULT_CONFIG_FNAME "config.txt"
#define DEFAULT_MODEL_FNAME "model.txt"
#define DEFAULT_DATA_FNAME "data.txt"

SimpleTimerInterface *timers = nullptr;

void parseInput(int argc, char **argv, string &modelFName, string &dataFName,
                int &NdDownsampled, string &outputFName, GoICP &goicp);
// void readConfig(string FName, GoICP &goicp);
int loadPointCloud(string FName, int &N, POINT3D **p);

/* void supervisor_func(){
  using namespace std::chrono_literals;
  std::this_thread::sleep_for(12*60s);
  std::cout << "reaching 12*60s...." << std::endl;
  std::exit(12);
} */

int main(int argc, char **argv) {
  std::vector<std::string> timer_names = {"build time", "register time",

                                          "total time"};

  if (!createTimerWithName(&timers, timer_names, timer_names.size())) {
    std::cout << "Failed to create timer" << std::endl;
    return -1;
  }

  startTimer(&timers, 2);
  int Nm, Nd, NdDownsampled;
  // clock_t clockBegin, clockEnd;
  string modelFName, dataFName, configFName, outputFname;
  POINT3D *pModel, *pData;
  GoICP goicp;

  parseInput(argc, argv, modelFName, dataFName, NdDownsampled, outputFname,
             goicp);
  // readConfig(configFName, goicp);

  // Load model and data point clouds
  loadPointCloud(modelFName, Nm, &pModel);
  loadPointCloud(dataFName, Nd, &pData);

  goicp.pModel = pModel;
  goicp.Nm = Nm;
  goicp.pData = pData;
  goicp.Nd = Nd;

  // Build Distance Transform
  cout << "# Building Distance Transform..." << flush;
  // clockBegin = clock();
  startTimer(&timers, 0);
  goicp.BuildDT();
  stopTimer(&timers, 0);
  double build_time = getTimerElapsed(&timers, 0);
  // clockEnd = clock();
  // cout << (double)(clockEnd - clockBegin) / CLOCKS_PER_SEC << "s (CPU)" <<
  // endl; cout << (double)(clockEnd - clockBegin) / CLOCKS_PER_SEC  << endl;
  cout << build_time << "s (CPU)" << endl;
  cout << build_time << endl;

  // Run GO-ICP
  if (NdDownsampled > 0) {
    goicp.Nd = NdDownsampled; // Only use first NdDownsampled data points
                              // (assumes data points are randomly ordered)
  }
  cout << "# Model ID: " << modelFName << " (" << goicp.Nm
       << "), Data ID: " << dataFName << " (" << goicp.Nd << ")" << endl;
  cout << "# Registering..." << endl;
  // cout << modelFName << endl;
  // cout << dataFName << endl;
  // auto f = std::thread{supervisor_func};
  // clockBegin = clock();
  startTimer(&timers, 1);
  goicp.Register();
  stopTimer(&timers, 1);
  double register_time = getTimerElapsed(&timers, 1);
  // clockEnd = clock();
  // double time = (double)(clockEnd - clockBegin) / CLOCKS_PER_SEC;
  cout << "# Optimal Rotation Matrix:" << endl;
  cout << goicp.optR << endl;
  cout << "# Optimal Translation Vector:" << endl;
  cout << goicp.optT << endl;
  cout << "# Finished in " << register_time << endl;
  cout << register_time << endl;
  cout << "# Registration Success!" << endl;
  cout << "1" << endl;

  // ofstream ofile;
  // ofile.open(outputFname.c_str(), ofstream::out);
  // ofile << time << endl;
  // ofile << goicp.optR << endl;
  // ofile << goicp.optT << endl;
  // ofile.close();

  delete (pModel);
  delete (pData);

  stopTimer(&timers, 2);
  double total_time = getTimerElapsed(&timers, 2);
  cout << "# Total time: " << total_time << "s (CPU)" << endl;
  cout << total_time << endl;
  timers = nullptr;
  // f.join();

  return 0;
}

void parseInput(int argc, char **argv, string &modelFName, string &dataFName,
                int &NdDownsampled, string &outputFName, GoICP &goicp) {
  // Set default values
  modelFName = DEFAULT_MODEL_FNAME;
  dataFName = DEFAULT_DATA_FNAME;
  outputFName = DEFAULT_OUTPUT_FNAME;
  NdDownsampled = 0; // No downsampling

  // cout << endl;
  // cout << "USAGE:" << "./GOICP <MODEL FILENAME> <DATA FILENAME> <NUM
  // DOWNSAMPLED DATA POINTS> <CONFIG FILENAME> <OUTPUT FILENAME>" << endl; cout
  // << endl;

  // 12 + 6 - 1  = 17 variable

  if (argc > 16) {

    goicp.MSEThresh = std::atof(argv[5]);
    goicp.initNodeRot.a = std::atof(argv[6]);
    goicp.initNodeRot.b = std::atof(argv[7]);
    goicp.initNodeRot.c = std::atof(argv[8]);
    goicp.initNodeRot.w = std::atof(argv[9]);
    goicp.initNodeTrans.x = std::atof(argv[10]);
    goicp.initNodeTrans.y = std::atof(argv[11]);
    goicp.initNodeTrans.z = std::atof(argv[12]);
    goicp.initNodeTrans.w = std::atof(argv[13]);
    goicp.trimFraction = std::atof(argv[14]);
    // If < 0.1% trimming specified, do no trimming
    if (goicp.trimFraction < 0.001) {
      goicp.doTrim = false;
    }
    goicp.dt.SIZE = std::atoi(argv[15]);
    goicp.dt.expandFactor = std::atof(argv[16]);

    cout << "# parameters" << endl;
    for (int i = 5; i <= 16; i++) {
      cout << argv[i] << endl;
    }
  } else {
    cout << "# You must provide arguments via commands args" << endl;
    cout << "# USAGE:"
         << "./GOICP <MODEL FILENAME> <DATA FILENAME> <NUMDOWNSAMPLED DATA "
            "POINTS> <OUTPUT FILENAME> + 12 arguments"
         << endl;
    std::exit(1);
    ;
  }
  if (argc > 4) {
    outputFName = argv[4];
  }
  if (argc > 3) {
    NdDownsampled = atoi(argv[3]);
  }
  if (argc > 2) {
    dataFName = argv[2];
  }
  if (argc > 1) {
    modelFName = argv[1];
  }

  cout << modelFName << endl;
  cout << dataFName << endl;

  cout << "# INPUT:" << endl;
  cout << "# (modelFName)->(" << modelFName << ")" << endl;
  cout << "# (dataFName)->(" << dataFName << ")" << endl;
  cout << "# (NdDownsampled)->(" << NdDownsampled << ")" << endl;
  cout << "# (outputFName)->(" << outputFName << ")" << endl;
  cout << endl;
}

/* void readConfig(string FName, GoICP &goicp) {
  // Open and parse the associated config file
  ConfigMap config(FName.c_str());

  // 12 variable
  goicp.MSEThresh = config.getF("MSEThresh");
  goicp.initNodeRot.a = config.getF("rotMinX");
  goicp.initNodeRot.b = config.getF("rotMinY");
  goicp.initNodeRot.c = config.getF("rotMinZ");
  goicp.initNodeRot.w = config.getF("rotWidth");
  goicp.initNodeTrans.x = config.getF("transMinX");
  goicp.initNodeTrans.y = config.getF("transMinY");
  goicp.initNodeTrans.z = config.getF("transMinZ");
  goicp.initNodeTrans.w = config.getF("transWidth");
  goicp.trimFraction = config.getF("trimFraction");
  // If < 0.1% trimming specified, do no trimming
  if (goicp.trimFraction < 0.001) {
    goicp.doTrim = false;
  }
  goicp.dt.SIZE = config.getI("distTransSize");
  goicp.dt.expandFactor = config.getF("distTransExpandFactor");

  cout << "CONFIG:" << endl;
  config.print();
  // cout << "(doTrim)->(" << goicp.doTrim << ")" << endl;
  cout << endl;
} */

int loadPointCloud(string FName, int &N, POINT3D **p) {
  int i;
  ifstream ifile;

  ifile.open(FName.c_str(), ifstream::in);
  if (!ifile.is_open()) {
    cout << "Unable to open point file '" << FName << "'" << endl;
    exit(-1);
  }
  ifile >> N; // First line has number of points to follow
  *p = (POINT3D *)malloc(sizeof(POINT3D) * N);
  for (i = 0; i < N; i++) {
    ifile >> (*p)[i].x >> (*p)[i].y >> (*p)[i].z;
  }

  ifile.close();

  return 0;
}
