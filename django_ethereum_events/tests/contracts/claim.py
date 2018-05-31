CLAIM_SOURCE = """
pragma solidity ^0.4.22;

contract Claim {
    mapping (address => mapping (bytes32 => bytes32)) claims;
    
    event ClaimSet(address indexed owner, bytes32 key, bytes32 value);
    
    function setClaim(bytes32 key, bytes32 value) public {
        claims[msg.sender][key] = value;
        emit ClaimSet(msg.sender, key, value);
    }
    
    function getClaim(bytes32 key) public view returns (bytes32) {
        return claims[msg.sender][key];
    }
}
"""

CLAIM_BYTECODE = "608060405234801561001057600080fd5b50610234806100206000396000f30060806040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063c9100bcb14610051578063d8d98c7b1461009e575b600080fd5b34801561005d57600080fd5b5061008060048036038101908080356000191690602001909291905050506100dd565b60405180826000191660001916815260200191505060405180910390f35b3480156100aa57600080fd5b506100db6004803603810190808035600019169060200190929190803560001916906020019092919050505061013e565b005b60008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008360001916600019168152602001908152602001600020549050919050565b806000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000846000191660001916815260200190815260200160002081600019169055503373ffffffffffffffffffffffffffffffffffffffff167f32e23ce2e82f46f421b8ffb2c7c2e2fa3db44ade2ac5f6796f52db108a887c5b838360405180836000191660001916815260200182600019166000191681526020019250505060405180910390a250505600a165627a7a72305820c63effc0a159f423f82dea3b99dadec63f2f1c069e06043d538fb09850eb41710029"

CLAIM_ABI_RAW = """
[
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": false,
				"name": "key",
				"type": "bytes32"
			},
			{
				"indexed": false,
				"name": "value",
				"type": "bytes32"
			}
		],
		"name": "ClaimSet",
		"type": "event"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "key",
				"type": "bytes32"
			},
			{
				"name": "value",
				"type": "bytes32"
			}
		],
		"name": "setClaim",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "key",
				"type": "bytes32"
			}
		],
		"name": "getClaim",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]
"""