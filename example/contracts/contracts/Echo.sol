pragma solidity ^0.4.22;

contract Echo {
    event LogEcho(string message, address sender, uint timestamp);

    function echo(string message) public {
        emit LogEcho(message, msg.sender, now);
    }
}
