BANK_SOURCE = """
pragma solidity ^0.4.22;

contract Bank {
    mapping (address => uint) balances;
    
    event LogWithdraw(address indexed owner, uint amount);
    event LogDeposit(address indexed owner, uint amount);
    
    constructor() public payable {}
    
    function withdraw(uint amount) public {
        require(balances[msg.sender] >= amount);
        balances[msg.sender] -= amount;
        msg.sender.transfer(amount);
        emit LogWithdraw(msg.sender, amount);
    }
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
        emit LogDeposit(msg.sender, msg.value);
    }
    
    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }
}
"""

BANK_BYTECODE = "60806040526102fd806100136000396000f300608060405260043610610057576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806312065fe01461005c5780632e1a7d4d14610087578063d0e30db0146100b4575b600080fd5b34801561006857600080fd5b506100716100be565b6040518082815260200191505060405180910390f35b34801561009357600080fd5b506100b260048036038101908080359060200190929190505050610104565b005b6100bc610235565b005b60008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054905090565b806000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020541015151561015157600080fd5b806000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055503373ffffffffffffffffffffffffffffffffffffffff166108fc829081150290604051600060405180830381858888f193505050501580156101e3573d6000803e3d6000fd5b503373ffffffffffffffffffffffffffffffffffffffff167f4ce7033d118120e254016dccf195288400b28fc8936425acd5f17ce2df3ab708826040518082815260200191505060405180910390a250565b346000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055503373ffffffffffffffffffffffffffffffffffffffff167f1b851e1031ef35a238e6c67d0c7991162390df915f70eaf9098dbf0b175a6198346040518082815260200191505060405180910390a25600a165627a7a723058207a9042b8bc4ad16515236e357784320ed78b4b74c0102cff6a8f61d11cebe5250029"

BANK_ABI_RAW = """
[
	{
		"constant": false,
		"inputs": [],
		"name": "deposit",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
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
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "LogWithdraw",
		"type": "event"
	},
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
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "LogDeposit",
		"type": "event"
	},
	{
		"inputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "constructor"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "withdraw",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getBalance",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]
"""
