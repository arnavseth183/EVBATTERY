// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./RiskManager.sol";
import "./PortfolioManager.sol";
import "./OracleInterface.sol";
import "./CircuitBreaker.sol";
import "./ProtocolStorage.sol";

/*
Governance
==========
DAO-based proposal system
Aligned with system parameters:
- Confidence threshold (τ)
- Transaction cost
- Slippage
- Circuit breaker threshold
*/

contract Governance is ProtocolStorage {

    // --------------------------------------------------
    // STRUCT
    // --------------------------------------------------

    struct Proposal {
        uint256 id;
        string description;

        string parameter;     // NEW: parameter to modify
        uint256 newValue;     // NEW: proposed value

        uint256 votesFor;
        uint256 votesAgainst;
        uint256 deadline;
        bool executed;
    }

    uint256 public nextProposalId;

    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public voted;

    // --------------------------------------------------
    // EVENTS
    // --------------------------------------------------

    event ProposalCreated(uint256 id, string parameter, uint256 value);
    event Voted(uint256 id, address voter, bool support);
    event ProposalExecuted(uint256 id, string parameter, uint256 value);

    // --------------------------------------------------
    // CREATE PROPOSAL
    // --------------------------------------------------

    function createProposal(
        string calldata description,
        string calldata parameter,
        uint256 newValue,
        uint256 duration
    )
        external
        onlyGovernance
    {
        proposals[nextProposalId] = Proposal({
            id: nextProposalId,
            description: description,
            parameter: parameter,
            newValue: newValue,
            votesFor: 0,
            votesAgainst: 0,
            deadline: block.timestamp + duration,
            executed: false
        });

        emit ProposalCreated(nextProposalId, parameter, newValue);
        nextProposalId++;
    }

    // --------------------------------------------------
    // VOTING
    // --------------------------------------------------

    function vote(uint256 proposalId, bool support) external {

        Proposal storage p = proposals[proposalId];

        require(block.timestamp < p.deadline, "Voting ended");
        require(!voted[proposalId][msg.sender], "Already voted");

        voted[proposalId][msg.sender] = true;

        if (support) {
            p.votesFor++;
        } else {
            p.votesAgainst++;
        }

        emit Voted(proposalId, msg.sender, support);
    }

    // --------------------------------------------------
    // EXECUTION (CRITICAL FIX)
    // --------------------------------------------------

    function executeProposal(uint256 proposalId) external {

        Proposal storage p = proposals[proposalId];

        require(block.timestamp >= p.deadline, "Voting not ended");
        require(!p.executed, "Already executed");
        require(p.votesFor > p.votesAgainst, "Not approved");

        // --------------------------------------------------
        // APPLY CHANGES (LINKED TO YOUR SYSTEM)
        // --------------------------------------------------

        bytes32 param = keccak256(bytes(p.parameter));

        if (param == keccak256("CONFIDENCE_THRESHOLD")) {
            confidenceThreshold = p.newValue; // τ
        }

        else if (param == keccak256("TRANSACTION_COST")) {
            transactionCost = p.newValue;
        }

        else if (param == keccak256("SLIPPAGE")) {
            slippage = p.newValue;
        }

        else if (param == keccak256("CIRCUIT_BREAKER_THRESHOLD")) {
            circuitBreakerThreshold = p.newValue;
        }

        else {
            revert("Invalid parameter");
        }

        p.executed = true;

        emit ProposalExecuted(proposalId, p.parameter, p.newValue);
    }
}