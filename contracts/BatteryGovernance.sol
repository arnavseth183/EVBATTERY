// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BatteryGovernance
 * @dev Governance contract for EV Battery Passport system
 * Manages protocol parameters and system settings
 */
contract BatteryGovernance {

    // --------------------------------------------------
    // STRUCTS
    // --------------------------------------------------

    struct Proposal {
        uint256 id;
        address proposer;
        string parameter;
        uint256 newValue;
        uint256 currentValue;
        uint256 votesFor;
        uint256 votesAgainst;
        mapping(address => bool) hasVoted;
        uint256 createdAt;
        uint256 deadline;
        bool executed;
        bool approved;
    }

    // --------------------------------------------------
    // STORAGE
    // --------------------------------------------------

    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;
    
    address public batteryPassportContract;
    address public admin;

    // Protocol parameters
    uint256 public maxBatteryAge = 365 days; // Maximum battery age for registration
    uint256 public minSohThreshold = 60; // Minimum SoH for active status
    uint256 public maxTemperatureThreshold = 60; // Maximum temperature warning
    uint256 public votingPeriod = 7 days; // Default voting period

    // --------------------------------------------------
    // EVENTS
    // --------------------------------------------------

    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        string parameter,
        uint256 newValue
    );
    
    event Voted(
        uint256 indexed proposalId,
        address indexed voter,
        bool support
    );
    
    event ProposalExecuted(
        uint256 indexed proposalId,
        string parameter,
        uint256 newValue
    );
    
    event ParameterUpdated(
        string parameter,
        uint256 oldValue,
        uint256 newValue
    );

    // --------------------------------------------------
    // MODIFIERS
    // --------------------------------------------------

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    modifier onlyBatteryPassport() {
        require(msg.sender == batteryPassportContract, "Only battery passport contract");
        _;
    }

    // --------------------------------------------------
    // CONSTRUCTOR
    // --------------------------------------------------

    constructor() {
        admin = msg.sender;
    }

    // --------------------------------------------------
    // ADMIN FUNCTIONS
    // --------------------------------------------------

    function setBatteryPassportContract(address _batteryPassportContract) external onlyAdmin {
        batteryPassportContract = _batteryPassportContract;
    }

    function updateAdmin(address newAdmin) external onlyAdmin {
        admin = newAdmin;
    }

    // --------------------------------------------------
    // PARAMETER MANAGEMENT
    // --------------------------------------------------

    function updateParameterDirectly(
        string calldata parameter,
        uint256 newValue
    ) external onlyAdmin {
        uint256 oldValue;
        
        return _updateParameter(parameter, newValue, oldValue);
    }

    function _updateParameter(
        string calldata parameter,
        uint256 newValue,
        uint256 oldValue
    ) internal returns (uint256) {
        if (keccak256(bytes(parameter)) == keccak256(bytes("maxBatteryAge"))) {
            oldValue = maxBatteryAge;
            maxBatteryAge = newValue;
        } else if (keccak256(bytes(parameter)) == keccak256(bytes("minSohThreshold"))) {
            oldValue = minSohThreshold;
            minSohThreshold = newValue;
        } else if (keccak256(bytes(parameter)) == keccak256(bytes("maxTemperatureThreshold"))) {
            oldValue = maxTemperatureThreshold;
            maxTemperatureThreshold = newValue;
        } else if (keccak256(bytes(parameter)) == keccak256(bytes("votingPeriod"))) {
            oldValue = votingPeriod;
            votingPeriod = newValue;
        } else {
            revert("Unknown parameter");
        }

        emit ParameterUpdated(parameter, oldValue, newValue);
        return oldValue;
    }

    function getParameter(string calldata parameter) external view returns (uint256) {
        if (keccak256(bytes(parameter)) == keccak256(bytes("maxBatteryAge"))) {
            return maxBatteryAge;
        } else if (keccak256(bytes(parameter)) == keccak256(bytes("minSohThreshold"))) {
            return minSohThreshold;
        } else if (keccak256(bytes(parameter)) == keccak256(bytes("maxTemperatureThreshold"))) {
            return maxTemperatureThreshold;
        } else if (keccak256(bytes(parameter)) == keccak256(bytes("votingPeriod"))) {
            return votingPeriod;
        } else {
            revert("Unknown parameter");
        }
    }

    // --------------------------------------------------
    // GOVERNANCE PROPOSALS
    // --------------------------------------------------

    function createProposal(
        string calldata parameter,
        uint256 newValue
    ) external returns (uint256) {
        uint256 currentValue = getParameter(parameter);
        
        proposalCount++;
        Proposal storage proposal = proposals[proposalCount];
        
        proposal.id = proposalCount;
        proposal.proposer = msg.sender;
        proposal.parameter = parameter;
        proposal.newValue = newValue;
        proposal.currentValue = currentValue;
        proposal.createdAt = block.timestamp;
        proposal.deadline = block.timestamp + votingPeriod;
        proposal.executed = false;
        proposal.approved = false;

        emit ProposalCreated(proposalCount, msg.sender, parameter, newValue);

        return proposalCount;
    }

    function voteOnProposal(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        
        require(proposal.id != 0, "Proposal not found");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        require(block.timestamp <= proposal.deadline, "Voting ended");
        
        proposal.hasVoted[msg.sender] = true;
        
        if (support) {
            proposal.votesFor++;
        } else {
            proposal.votesAgainst++;
        }

        emit Voted(proposalId, msg.sender, support);
    }

    function executeProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        
        require(proposal.id != 0, "Proposal not found");
        require(!proposal.executed, "Already executed");
        require(block.timestamp > proposal.deadline, "Voting not ended");
        require(proposal.votesFor > proposal.votesAgainst, "Proposal not approved");
        
        proposal.executed = true;
        proposal.approved = true;
        
        _updateParameter(proposal.parameter, proposal.newValue, proposal.currentValue);

        emit ProposalExecuted(proposalId, proposal.parameter, proposal.newValue);
    }

    // --------------------------------------------------
    // QUERY FUNCTIONS
    // --------------------------------------------------

    function getProposal(uint256 proposalId) 
        external 
        view 
        returns (
            uint256 id,
            address proposer,
            string memory parameter,
            uint256 newValue,
            uint256 currentValue,
            uint256 votesFor,
            uint256 votesAgainst,
            uint256 createdAt,
            uint256 deadline,
            bool executed,
            bool approved
        ) 
    {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "Proposal not found");
        
        return (
            proposal.id,
            proposal.proposer,
            proposal.parameter,
            proposal.newValue,
            proposal.currentValue,
            proposal.votesFor,
            proposal.votesAgainst,
            proposal.createdAt,
            proposal.deadline,
            proposal.executed,
            proposal.approved
        );
    }

    function getAllProposals() external view returns (uint256[] memory) {
        uint256[] memory proposalIds = new uint256[](proposalCount);
        for (uint256 i = 0; i < proposalCount; i++) {
            proposalIds[i] = i + 1;
        }
        return proposalIds;
    }
}
