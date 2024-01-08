# Project For Donation Management

## Overview

Welcome to Project For Donation Management! This Django application is designed for Donation management system.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)

## Getting Started

### Prerequisites

Make sure you have the following software and dependencies installed before running the application:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/your-django-app.git
    cd your-django-app
    ```

### **_NOTE:_**
- Install Docker for easy setup.

2. Create virtual enviroment,

    ````
    python3 -m venv <env_name>
    ````
    - For windows:
        ````
        .<env_name>\Scripts\activate  
        ````

    -   For Ubantu/mac

        ````
        source <env_name>/bin/activate
        ````
3. For run docker
    ````
    docker-compose up --build
    ````

### Running the Application

Start the application using Docker Compose:

````
docker-compose up
````

## API SPECS


### **_NOTE:_**
- Added postman collection in repo, please import it in your postman, Just replace,
````
{{ baseurl }}
```` 
variable and can check all end-points listed below. 

### OnBoard User
- User can register them selfs for donation by send_otp and verify_otp end-points.
- The flow is provide phone number we sent you an OTP and get the token by passing the OTP by verify_otp end-point.

### Choose Payment Gateway
- User can choose payment gateway option with update_payment_gateway end-point.
    - options available
        -   Stripe_payment
        -   Razorpay_payment

### Get Payment (Checkout) Link
- Get checkout link by donate_amount end-point.

### Get Payment History For User
- Get payment history for specific time interval

### For Data visualization 
- please check donation_chart end-point.

