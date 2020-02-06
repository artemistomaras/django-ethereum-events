const truffleAssert = require('truffle-assertions');
const Echo = artifacts.require('Echo');

contract('Echo', accounts => {
    let echoContract;

    it('should be able to echo a message', async () => {
        let message = "hello world!"
        let tx = await echoContract.echo(accounts[2], details, timestamp, {from: owner})

        truffleAssert.eventEmitted(tx, 'LogEcho', (ev) => {
            return ev.message == message;
        });
    });

    beforeEach(async () => {
        echoContract = await Echo.new({from: accounts[0]})
    })


});
