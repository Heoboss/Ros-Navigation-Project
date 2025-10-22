# 🤖 ROS를 이용한 자율 주행 로봇 내비게이션 프로젝트 

이 프로젝트는 **ROS (Robot Operating System)**를 기반으로 실제 환경에서 로봇이 스스로 지도를 생성하고(SLAM), 지정된 목적지까지 장애물을 피해 자율 주행하는 내비게이션 시스템을 구현한 것입니다.<br/>

check my velog : https://velog.io/@pas901/series/%EC%A1%B8%EC%97%85%EC%9E%91%ED%92%88

Youtube link : https://www.youtube.com/@2024_final_ros_project_konkuk


<h2> Hardware we used</h2>

- Rplidar A1M8 - link : https://www.devicemart.co.kr/goods/view?no=1149202

- Arduino Uno
  
- PCA9685 (16 Channel pwm servo driver) - link : https://www.devicemart.co.kr/goods/view?no=1382245
  
- Raspberry Pi 4 8GB
  
- Mecanum Wheel 100mm - link : https://www.devicemart.co.kr/goods/view?no=1272497
  
- linear motor (lift) - link : https://ko.aliexpress.com/item/1005005862509864.html?spm=a2g0o.order_list.order_list_main.10.21ef140fj03eFd&gatewayAdapt=glo2kor


---

## 🤖 로봇 사진

<img width="1225" height="577" alt="image" src="https://github.com/user-attachments/assets/eea190bb-d866-4823-b7b0-7a8291856112" />

---

## 📖 목차

* [프로젝트 목표](#-프로젝트-목표)
* [주요 기능](#-주요-기능)
* [개발 환경 및 사용 기술](#-개발-환경-및-사용-기술)
* [패키지 구조](#-패키지-구조)
* [핵심 노드 및 토픽](#-핵심-노드-및-토픽)
* [결과 및 시연](#-결과-및-시연)

---

## 🎯 프로젝트 목표

* **SLAM (Simultaneous Localization and Mapping)**: 실제 시연환경에서 커스텀 로봇을 이용하여 미지의 환경을 탐험하고, 2D 지도를 생성합니다.
* **Localization (위치 추정)**: 생성된 지도를 바탕으로 `AMCL` 패키지를 사용하여 로봇의 현재 위치를 정확하게 추정합니다.
* **Path Planning (경로 계획)**: `move_base` 패키지를 통해 목적지(Goal)가 주어졌을 때, 지도와 로봇의 위치를 기반으로 최적의 경로를 계획합니다.
* **Obstacle Avoidance (장애물 회피)**: 주행 중 Lidar 센서로 감지되는 동적/정적 장애물을 실시간으로 회피하며 안정적으로 목적지까지 이동합니다.

---

## ✨ 주요 기능

* **지도 생성**: `hectorslam` 패키지를 활용한 2D Occupancy Grid Map 생성
* **위치 추정**: `AMCL (Adaptive Monte Carlo Localization)`을 이용한 실시간 로봇 위치 추정
* **경로 계획**: Global Planner (e.g., A\*)와 Local Planner (e.g., DWA)를 이용한 경로 생성
* **시각화**: `RViz`를 통해 지도, 로봇의 위치, 센서 데이터, 경로 등을 실시간으로 시각화

---

## 🛠️ 개발 환경 및 사용 기술

* **OS**: Ubuntu 20.04 LTS
* **ROS Version**: ROS Noetic
* **Visualization**: RViz
* **Robot Model**: Custom Robot

#### ROS Packages
* `cartographer`: SLAM
* `amcl`: Localization
* `move_base`: Navigation
* `map_server`: Map saving/loading

---


## 동작영상

아래 이미지를 클릭하면 Youtube로 이동하여 프로젝트 동작 영상을 확인할 수 있습니다.

[![프로젝트 동작 영상](https://img.youtube.com/vi/RS3TgxG2GQo/hqdefault.jpg)](https://youtu.be/RS3TgxG2GQo)
