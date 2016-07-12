# Control de Producción
This Django project was developed for a printing company in Guatemala City, Guatemala called [Digital House GT](http://digitalhousegt.com). This project integrates itself with the company's database to obtain relevant information about the orders being processed. Along with that information, this module allows users to keep control over the state of the order from start to finish.


## Motivation
I was given the task to make it easy to visualize the processes completed and left to complete for each order. My initial idea was to develop a Java application to solve this problem. However, I opted not to use Java because a JVM installation would be required, and also because I needed an easy way to develop a user-friendly Graphical Interface, which is not something Java is known for.

My second idea was to develop a Django web application to solve this proble. This idea was clearly the best one for this problem because I could easily create Graphical Interfaces using HTML and CSS. Nevertheless, I was still required to download a Python interpreter to run the program locally, but Django was still a much better option.

This is why I was motivated to use Django to solve the problem the client described.


## Problem it solved
This module targets a huge problem Digital House GT encountered: not knowing exactly what orders are being processed, and how much more time an order would require before it is fulfilled (in terms of processes left).

This problem was solved by allowing the employees to change the state of an order, while this change of state is displayed in a table for the manager to see (examples below).


## Views
This Django app has four main views. Each one has a specific functionality that allows the user to do different things.

#### List of Orders
This view allows for the user to see a list of all the orders stored. Through this page, the user can access the detail page of a specific order.

![List of Orders page](https://drive.google.com/uc?id=0Bx5ecVUu5VhJUVpub0pmOWlLaWM)

#### Order Detail
This view allows for the user to see all the processes this order must go through. It counts with two subviews:

- Processes

  In this view, the user is able to *start*, *pause*, *resume*, and *finish* each process. 

![Processes subview in Order Detail page](https://drive.google.com/uc?id=0Bx5ecVUu5VhJY2swcVNyUHd1bnM)

- Analytics

  In this view, the manager is able to see the time it took to finish each of the processes, as well as the total time each process was paused.

![Analytics subview in Order Detail page](https://drive.google.com/uc?id=0Bx5ecVUu5VhJUE44bG5HdGl1MDg)

#### Analytics
The Analytics page displays some valuable stats, completion times, and much more. It counts with several subviews:

- Processes

  In this view, the manager is able to see what is the average time to complete a process (this is standardized by calculating the average time to complete one unit of the total quantity of the order).

![Processes subview in Analytics page](https://drive.google.com/uc?id=0Bx5ecVUu5VhJck5NVzJiQVkteFE)

- Machines

  In this view, the manager is able to see the number of printed sheets in the last 7 days, last 30 days, and overall. This metric is relevant because it allows the manager to see which printing machine has greater demand and when.

![Machines subview in Analytics page](https://drive.google.com/uc?id=0Bx5ecVUu5VhJUEFPWW9yaEZxeVk)

- Clients

  In this view, the manager is able to the number of orders each clients has requested in the last 7 days, last 30 days, and overall. This metric seeks to show which are the top five clients in each of the time ranges mentioned before.

![Clients subview in Analytics page](https://drive.google.com/uc?id=0Bx5ecVUu5VhJMnJnQUM2NEQtT2M)

- Employees

  In this view, the manager is able to see all of the processes finished by each employee and the average time (per unit, as explained in the Processes subview) for each finished process. This metric is *extremely important* because the manager is able to see the productivity of each employee and thus is able to better delegate responsility among the employees.

![Workers subview in Analytics page](https://drive.google.com/uc?id=0Bx5ecVUu5VhJU3FYOHpxajlHdlk)

#### Active Orders
This view displays the state of each order that has not been finished. This view *solves the client's problem* of not being able to visualize what orders are being processed, and how close to being done each order is.

![Active Orders page](https://drive.google.com/uc?id=0Bx5ecVUu5VhJbmxZa1ExYThRWGc)

The table displayed refreshes every minute (with the use of JavaScript) in order to accurately display the state of each order.


## Tests
This project was thoroughly tested with the use of many testing tools:

- _Unit testing_:
Each view was tested by itself, as well as each method of all the Analytics metrics.

- _Selenium_:
This testing tool allowed for better testing of the Graphical Interface. Through the use of Selenium, I was able to thoroughly test the correct behavior of each component of each view.

- _Coverage_:
This tool allowed for a more robust and complete testing. It revealed "else" cases and views that were not being tested (mainly views that were accesed through a POST request).


## Future changes
Tasks in the backlog:
- Add user login
- Add more metrics in the Analytics page
- Host this app in the web (potentially with Heroku)


## License
MIT License

Copyright (c) 2016 Andy Sapper

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgements
This project was possible thanks to the input of all the workers at Digital House GT, as well as all the great support from the Django community by providing modules and answers for common problems encountered by developers.
