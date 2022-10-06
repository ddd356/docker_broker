# docker_broker

Build and start docker container with:
```
docker-compose up --build
```
Wait initialization. When it's done you will see a message " __* Running on http://127.0.0.1:5000"__
![image](https://user-images.githubusercontent.com/5135143/194400263-9601581e-ab90-4ea7-ac3b-e49071bf464c.png)

## Test a server with a Curl from container CLI.
Curl requests will return you a transaction ID.

1. Put 1000.0 on to a client with id 1
```
curl "http://127.0.0.1:5000/1/1000.0/put"
```
2. Withdraw 600.0 from the same client
```
curl "http://127.0.0.1:5000/1/600.0/withdraw"
```
3. Try withdraw another 600.0 from the same client
```
curl "http://127.0.0.1:5000/1/600.0/withdraw"
```
The last request will be cancelled because of low credits.

## Look a result at Postgre database
Use db's container CLI.

1. Connect to the database
```
psql postgres://postgres:pg@localhost:5432/accounts
```
2. Look at the __history__ table
```
SELECT * FROM history;
```
![image](https://user-images.githubusercontent.com/5135143/194402451-1ee2289c-3f26-4992-955a-b37c68e52602.png)

You see two successfull transactions and one cancelled.

3. Look at the __accounts__ table
```
SELECT * FROM accounts;
````
![image](https://user-images.githubusercontent.com/5135143/194402732-ed5047e8-80e0-499d-ac5c-c50fb1588850.png)

You see 400 credits on the account of a client with ID=1.
