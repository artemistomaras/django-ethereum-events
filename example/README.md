Here is an example django app used for developing using a smart contract defined in ``contracts`` folder.

## Local usage
In one terminal, run the dev blockchain:

```bash
cd contracts
npm install
npm run dev-blockchain
```

In a second terminal, deploy the smart contract
```bash
cd contracts
npm run deploy-local
```

Install local package

```bash
pip3 install -e ../
```

Make migrations

```bash
python3 manage.py migrate
```

Register smart contract event(s)

```bash
python3 manage.py register_events
```

Send an `echo` transaction

```bash
python3 manage.py send_echo
```

Invoke the event listener, check that event was captured
```bash
python3 manage.py run_listener
```
