# Kubernetes 3-Node Cluster Examination

โครงการติดตั้งและทดสอบระบบ Web Application บน Kubernetes Cluster จำนวน 3 Nodes โดยใช้ Traefik Ingress Controller และ NGINX Reverse Proxy สำหรับให้บริการ Student Portal, Research Service, API Service และ Admin Portal

## 1. Student Information

- Student ID: 68130489
- Program: Master's Degree in Computer Engineering
- Namespace: `id-489`

## 2. Project Overview

โครงการนี้จัดทำขึ้นเพื่อศึกษาการติดตั้งและบริหารจัดการ Containerized Applications บน Kubernetes โดยครอบคลุมการสร้าง Container Image การติดตั้ง Deployment และ Service การกำหนดเส้นทางผ่าน Ingress การกระจาย Pods ระหว่าง Worker Nodes และการจัดเก็บข้อมูลด้วย PersistentVolume และ PersistentVolumeClaim

## 3. Kubernetes Architecture

| Node | IP Address | Role |
|---|---|---|
| k8s-control | 192.168.239.141 | Control Plane |
| k8s-worker1 | 192.168.239.142 | Worker Node |
| k8s-worker2 | 192.168.239.143 | Worker Node |

ระบบใช้ NGINX Reverse Proxy บน Control Plane เพื่อส่ง HTTP Requests ไปยัง Traefik Ingress Controller ซึ่งทำหน้าที่กำหนดเส้นทางไปยัง Kubernetes Services และ Pods ที่เกี่ยวข้อง

## 4. Application Services

| Application | URL | Description |
|---|---|---|
| Student Portal | http://www.iam-489.com/ | แสดงข้อมูลนักศึกษา |
| Research Service | http://www.iam-489.com/research | แสดงข้อมูลสรุปงานวิจัย |
| API Service | http://www.iam-489.com/api-489 | แสดงข้อความจาก API |
| Admin Portal | http://admin.iam-489.com/ | จัดการข้อมูลผ่านหน้า Admin |
| About Service | http://www.iam-489.com/about | หน้าแสดงข้อมูลเพิ่มเติม |

หมายเหตุ: เส้นทาง `/api-489` เป็นเส้นทางตามข้อกำหนดงาน และต้องตรวจสอบว่า Ingress รองรับเส้นทางดังกล่าวก่อนส่งงาน

## 5. Technologies

- Kubernetes
- Containerd
- Podman
- Traefik Ingress Controller
- NGINX Reverse Proxy
- Python Flask
- Gunicorn
- ConfigMap
- PersistentVolume (PV)
- PersistentVolumeClaim (PVC)

## 6. Project Structure

```text
k8s-exam-68130489/
├── apps/
│   ├── app-about/
│   ├── app-api/
│   ├── app-research/
│   └── portal-489/
├── configs/
│   ├── hosts-linux.txt
│   └── nginx.conf
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 01-storage.yaml
│   ├── 02-app-about-configmap.yaml
│   ├── 02-app-about-deployment.yaml
│   ├── 03-app-research.yaml
│   ├── 04-app-api.yaml
│   ├── 05-ingress.yaml
│   ├── 06-portal.yaml
│   └── 07-portal-ingress.yaml
├── .gitignore
└── README.md
```

## 7. Deployment Prerequisites

เตรียม Kubernetes Cluster จำนวน 3 Nodes โดยมี Control Plane 1 เครื่อง และ Worker Nodes 2 เครื่อง พร้อมติดตั้ง Kubernetes, Containerd, Podman และ NGINX ตามบทบาทของแต่ละเครื่อง

การติดตั้งนี้ใช้ Container Images ที่สร้างภายในระบบ Lab จึงต้องกระจาย Images ไปยัง Worker Nodes ก่อนใช้งาน Deployment

ตรวจสอบความพร้อมของ Cluster ด้วยคำสั่ง:

```bash
kubectl get nodes
```

## 8. Container Image Preparation

สร้าง Container Images บนเครื่อง `k8s-control`

```bash
podman build -t localhost/app-research:1.1 apps/app-research
podman build -t localhost/portal-489:1.1 apps/portal-489
```

บันทึก Images เป็นไฟล์ TAR

```bash
podman save -o /tmp/app-research-1.1.tar localhost/app-research:1.1
podman save -o /tmp/portal-489-1.1.tar localhost/portal-489:1.1
```

ส่ง Images ไปยัง Worker Nodes ที่เกี่ยวข้อง

```bash
scp /tmp/app-research-1.1.tar k8s-worker1:/tmp/
scp /tmp/portal-489-1.1.tar k8s-worker1:/tmp/
scp /tmp/portal-489-1.1.tar k8s-worker2:/tmp/
```

นำ Images เข้าสู่ Containerd บน Worker1

```bash
sudo ctr -n k8s.io images import /tmp/app-research-1.1.tar
sudo ctr -n k8s.io images import /tmp/portal-489-1.1.tar
```

บน Worker2

```bash
sudo ctr -n k8s.io images import /tmp/portal-489-1.1.tar
```

หมายเหตุ: ต้องเตรียม Images ของ API Service และบริการอื่นตามที่ระบุในไฟล์ Deployment ด้วย โดยคำสั่ง Import ให้ดำเนินการบน Worker Node ที่ต้องใช้งาน Image นั้น

## 9. Kubernetes Deployment

ดำเนินการบนเครื่อง `k8s-control` ภายในโฟลเดอร์โครงการ

### 9.1 Create Namespace

```bash
kubectl apply -f k8s/00-namespace.yaml
```

### 9.2 Configure Persistent Storage

```bash
kubectl apply -f k8s/01-storage.yaml
```

ตรวจสอบและเตรียมไดเรกทอรีจัดเก็บข้อมูลบน Worker Node ให้ตรงกับ PersistentVolume ที่กำหนดใน YAML

### 9.3 Deploy About Service

```bash
kubectl apply --server-side -f k8s/02-app-about-configmap.yaml
kubectl apply -f k8s/02-app-about-deployment.yaml
```

### 9.4 Deploy Research Service

```bash
kubectl apply -f k8s/03-app-research.yaml
```

### 9.5 Deploy API Service

```bash
kubectl apply -f k8s/04-app-api.yaml
```

### 9.6 Deploy Student Portal

```bash
kubectl apply -f k8s/06-portal.yaml
```

## 10. Traefik Ingress Controller

ตัวอย่างการติดตั้ง Traefik ด้วย Helm

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
```

```bash
helm upgrade --install traefik traefik/traefik \
  --namespace traefik \
  --create-namespace \
  --set service.spec.type=NodePort \
  --set ports.web.nodePort=30080 \
  --set ingressClass.enabled=true
```

ติดตั้ง Ingress Resources

```bash
kubectl apply -f k8s/05-ingress.yaml
kubectl apply -f k8s/07-portal-ingress.yaml
```

ตรวจสอบ

```bash
kubectl get ingress -n id-489
```

## 11. NGINX Reverse Proxy

ติดตั้ง NGINX บน Control Plane

```bash
sudo apt update
sudo apt install nginx -y
```

นำไฟล์ Configuration ไปใช้งาน

```bash
sudo cp configs/nginx.conf /etc/nginx/sites-available/id-489.conf
```

```bash
sudo ln -sf /etc/nginx/sites-available/id-489.conf /etc/nginx/sites-enabled/id-489.conf
```

ตรวจสอบและโหลด Configuration

```bash
sudo nginx -t
sudo systemctl reload nginx
```

NGINX ทำหน้าที่รับ HTTP Requests ผ่าน Control Plane และส่งต่อไปยัง Traefik Ingress Controller บน Worker Nodes

## 12. Domain and Hosts Configuration

กำหนด Hosts บนเครื่อง Client ที่ใช้ทดสอบ

```text
192.168.239.141 www.iam-489.com
192.168.239.141 admin.iam-489.com
```

สำหรับ Windows ให้แก้ไขไฟล์:

```text
C:\Windows\System32\drivers\etc\hosts
```

จากนั้นเปิดเว็บไซต์ผ่าน Web Browser ภายในเครือข่าย Lab

## 13. Kubernetes Verification

ตรวจสอบสถานะ Nodes

```bash
kubectl get nodes
```

ตรวจสอบ Deployments

```bash
kubectl get deployments -n id-489
```

ตรวจสอบ Pods และตำแหน่ง Worker Nodes

```bash
kubectl get pods -n id-489 -o wide
```

ตรวจสอบ Services และ Ingress

```bash
kubectl get services -n id-489
kubectl get ingress -n id-489
```

ตรวจสอบ Persistent Storage

```bash
kubectl get pv
kubectl get pvc -n id-489
```

ตรวจสอบการอัปเดต Deployment

```bash
kubectl rollout status deployment/app-research -n id-489
kubectl rollout status deployment/portal-489 -n id-489
```

จากผลการทดสอบล่าสุด Deployment ทั้ง 4 รายการมี Pods รวม 8 ตัว อยู่ในสถานะ Running และ Ready โดย Student Portal กระจายอยู่บน Worker1 และ Worker2 ส่วน Research Service ทำงานบน Worker1 ตามการกำหนด Node Selector

## 14. Application Testing

ทดสอบการตอบสนองผ่าน NGINX Reverse Proxy

```bash
curl -I -H "Host: www.iam-489.com" http://192.168.239.141/
```

```bash
curl -I -H "Host: www.iam-489.com" http://192.168.239.141/research
```

```bash
curl -I -H "Host: www.iam-489.com" http://192.168.239.141/api-489
```

```bash
curl -I -H "Host: admin.iam-489.com" http://192.168.239.141/
```

```bash
curl -I -H "Host: admin.iam-489.com" http://192.168.239.141/edit
```

ผลที่คาดหวังคือ HTTP Status `200 OK` สำหรับเส้นทางที่กำหนด และต้องตรวจสอบเนื้อหาของแต่ละหน้าเพิ่มเติมผ่าน Web Browser

สำหรับ Admin Portal ให้ทดสอบการแก้ไขและบันทึกข้อมูล รวมถึงตรวจสอบการคงอยู่ของข้อมูล Research ภายหลังการ Restart Pod

## 15. Security Notice

โครงการนี้จัดทำขึ้นเพื่อการศึกษาและทดสอบภายในเครือข่าย Lab เท่านั้น ไม่ควรเผยแพร่ Admin Portal สู่เครือข่ายสาธารณะโดยไม่มีระบบ Authentication และการควบคุมสิทธิ์

ห้ามจัดเก็บ Password, Access Token, Private Key หรือข้อมูลลับใน Public GitHub Repository

## 16. Author

Student ID: 68130489

Master's Degree in Computer Engineering
