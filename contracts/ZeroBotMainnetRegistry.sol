// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ZeroBotMainnetRegistry {
    address public immutable owner;

    event ComputePurchased(
        address indexed buyer,
        string gpu,
        uint256 durationHours,
        string providerTag,
        uint256 value,
        uint256 timestamp
    );

    event StorageAnchored(
        address indexed buyer,
        string rootHash,
        string fileName,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "owner only");
        _;
    }

    constructor(address initialOwner) {
        require(initialOwner != address(0), "owner required");
        owner = initialOwner;
    }

    function purchaseCompute(
        string calldata gpu,
        uint256 durationHours,
        string calldata providerTag
    ) external payable {
        require(msg.value > 0, "value required");
        require(durationHours > 0, "duration required");
        emit ComputePurchased(
            msg.sender,
            gpu,
            durationHours,
            providerTag,
            msg.value,
            block.timestamp
        );
    }

    function anchorStorage(
        string calldata rootHash,
        string calldata fileName
    ) external {
        require(bytes(rootHash).length > 0, "root required");
        emit StorageAnchored(msg.sender, rootHash, fileName, block.timestamp);
    }

    function withdraw(address payable to, uint256 amount) external onlyOwner {
        require(to != address(0), "recipient required");
        require(amount <= address(this).balance, "insufficient balance");
        (bool ok, ) = to.call{value: amount}("");
        require(ok, "withdraw failed");
    }
}
