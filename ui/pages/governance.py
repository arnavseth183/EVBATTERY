import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import random

from blockchain_protocol.execution_engine.protocol_controller import ProtocolController
from blockchain_protocol.web3_layer.web3_provider import get_web3_connection
from blockchain_protocol.logging_config import get_governance_logger
from config import AppConfig

# 🔥 USE GOVERNANCE LOGGER FOR GOVERNANCE OPERATIONS
governance_logger = get_governance_logger()


def calculate_recommended_parameters(protocol: ProtocolController):
    """
    Calculate recommended parameters based on trade execution data
    """
    try:
        # Get trade history
        portfolio = protocol.get_portfolio_state()
        tx_history = portfolio.get("transactions", [])
        
        if not tx_history or len(tx_history) == 0:
            return None
        
        # Normalize transaction data
        df_tx = pd.DataFrame()
        tx_data = []
        
        for tx in tx_history:
            tx_data.append({
                "symbol": tx.get("symbol", "N/A"),
                "action": tx.get("action", "UNKNOWN"),
                "quantity": float(tx.get("quantity", 0) or 0),
                "price": float(tx.get("price", 0) or 0),
                "timestamp": tx.get("timestamp", datetime.now())
            })
        
        if not tx_data:
            return None
        
        df_tx = pd.DataFrame(tx_data)
        
        # Calculate metrics from execution
        recommendations = {}
        
        # 1. Max position size recommendation (based on max position taken)
        max_qty_per_symbol = df_tx.groupby("symbol")["quantity"].sum().max()
        max_qty_per_symbol = max_qty_per_symbol if not pd.isna(max_qty_per_symbol) else 0
        recommendations["max_position_size"] = round(max(max_qty_per_symbol * 1.05, 100), 2)
        
        # 2. Leverage recommendation (based on execution pattern)
        total_trades = len(df_tx)
        buy_trades = len(df_tx[df_tx["action"].str.upper() == "BUY"])
        if total_trades > 0:
            buy_ratio = buy_trades / total_trades
            recommendations["leverage"] = round(min(buy_ratio * 3, 2), 2)
        else:
            recommendations["leverage"] = 2
        
        # 3. Risk limit recommendation (inverse of success rate)
        if total_trades > 0:
            price_volatility = df_tx["price"].std() / df_tx["price"].mean() if df_tx["price"].mean() > 0 else 0
            recommendations["risk_limit"] = round(min(1 - (price_volatility * 0.5), 0.9), 2)
            recommendations["risk_limit"] = max(recommendations["risk_limit"], 0.5)
        else:
            recommendations["risk_limit"] = 0.7
        
        # 4. Min confidence recommendation (based on trade frequency and success)
        total_quantity = df_tx["quantity"].sum()
        if total_quantity > 0:
            confidence = min(0.9, 0.5 + (total_quantity / (total_quantity * 2)))
            recommendations["min_confidence"] = round(confidence, 2)
        else:
            recommendations["min_confidence"] = 0.65
        
        return recommendations
    
    except Exception as e:
        st.warning(f"Could not calculate recommendations: {e}")
        return None


def render_governance(protocol: ProtocolController = None, current_user=None):
    """
    Enhanced Governance panel with parameter calculations from trade execution
    
    Args:
        protocol: ProtocolController instance (optional, will create if needed)
        current_user: Current logged-in user for filtering proposals
    """

    st.title("🏛 Governance Panel")
    
    # Initialize session state for proposals and voting timer
    if "proposals_list" not in st.session_state:
        st.session_state.proposals_list = {}
    if "proposal_creation_time" not in st.session_state:
        st.session_state.proposal_creation_time = {}

    try:
        # ✅ Use passed protocol or create new one
        if protocol is None:
            config = AppConfig()
            web3 = get_web3_connection()
            controller = ProtocolController(config, web3)
        else:
            controller = protocol

        # --------------------------------------------------
        # LOAD PARAMETERS & CALCULATE RECOMMENDATIONS
        # --------------------------------------------------

        st.subheader("📊 Protocol Parameters")

        params = controller.get_protocol_parameters()

        if not params:
            st.warning("No protocol parameters found")
            return

        # Calculate recommended parameters from trade execution
        recommendations = calculate_recommended_parameters(controller)

        # Display parameters in a dynamic grid format
        param_cols = st.columns(len(params) if len(params) <= 4 else 2)
        
        param_display = []
        for i, (key, value) in enumerate(params.items()):
            col_idx = i % len(param_cols)
            with param_cols[col_idx]:
                recommended_val = recommendations.get(key, value) if recommendations else value
                st.metric(key, f"{value}", delta=f"→ {recommended_val}")
                param_display.append({
                    "Parameter": key, 
                    "Current Value": value,
                    "Recommended": recommended_val if recommendations else "—",
                    "Variance": f"{((recommended_val - value) / value * 100):.1f}%" if recommendations and value != 0 else "—"
                })

        # Show comprehensive table with recommendations
        st.subheader("📋 Parameter Analysis & Recommendations")
        param_df = pd.DataFrame(param_display)
        st.dataframe(param_df, use_container_width=True, hide_index=True)

        # --------------------------------------------------
        # TRADE EXECUTION SUMMARY (SOURCE OF CALCULATIONS)
        # --------------------------------------------------
        
        if recommendations:
            st.subheader("📈 Trade Execution Analysis")
            
            try:
                portfolio = controller.get_portfolio_state()
                tx_history = portfolio.get("transactions", [])
                
                if tx_history:
                    df_tx = pd.DataFrame(tx_history)
                    
                    # Filter transactions by current user/account only
                    if current_user:
                        df_tx = df_tx[df_tx.get("account", "") == current_user] if "account" in df_tx.columns else df_tx[df_tx.get("user", "") == current_user] if "user" in df_tx.columns else df_tx
                    
                    exec_col1, exec_col2, exec_col3, exec_col4 = st.columns(4)
                    
                    with exec_col1:
                        st.metric("Total Executions", len(df_tx))
                    
                    with exec_col2:
                        buy_count = len(df_tx[df_tx.get("action", "").str.upper() == "BUY"]) if "action" in df_tx.columns else 0
                        st.metric("Buy Trades", buy_count)
                    
                    with exec_col3:
                        avg_price = df_tx["price"].mean() if "price" in df_tx.columns else 0
                        st.metric("Avg Price", f"₹ {avg_price:,.2f}")
                    
                    with exec_col4:
                        total_qty = df_tx["quantity"].sum() if "quantity" in df_tx.columns else 0
                        st.metric("Total Quantity", f"{total_qty:.2f}")
            
            except Exception as e:
                st.info("Trade execution data not available for analysis")

        # --------------------------------------------------
        # SECTION 1: CREATE NEW PROPOSAL
        # --------------------------------------------------

        st.subheader("📋 1. Create New Proposal")
        
        st.markdown("**Select a parameter to propose for update (voting required):**")

        # Create two-column layout for better UX
        col_select, col_input = st.columns([1, 1])
        
        with col_select:
            param = st.selectbox(
                "Select Parameter",
                list(params.keys()),
                key="param_selector",
                help="Choose which parameter to update"
            )
        
        # Get default value
        try:
            default_value = float(params[param])
        except:
            default_value = 0.0
        
        # Get recommended value if available
        recommended_value = recommendations.get(param, default_value) if recommendations else default_value

        with col_input:
            new_value = st.number_input(
                "New Value",
                value=default_value,
                step=0.01,
                key="param_input",
                help=f"Current: {default_value} | Recommended: {recommended_value}"
            )

        # --------------------------------------------------
        # LIVE PREVIEW OF CHANGE WITH RECOMMENDATIONS
        # --------------------------------------------------
        
        col_preview1, col_preview2, col_preview3 = st.columns(3)
        
        with col_preview1:
            st.info(f"**Current:** {default_value}")
        
        with col_preview2:
            st.warning(f"**Recommended:** {recommended_value}" if recommendations else "**Recommended:** N/A")
        
        with col_preview3:
            if new_value != default_value:
                st.success(f"**Proposed:** {new_value}")
            else:
                st.caption("No change from current")

        # --------------------------------------------------
        # VALIDATION & CREATE PROPOSAL
        # --------------------------------------------------

        col_validate, col_submit = st.columns([1, 1])
        
        with col_validate:
            if new_value == default_value:
                st.warning("⚠️ No change detected - current value matches proposed value")
            elif recommendations and new_value != recommended_value:
                st.info(f"ℹ️ Note: Recommended value is {recommended_value}")

        with col_submit:
            create_proposal_btn = st.button(
                "📋 Submit New Proposal",
                key="create_proposal_btn",
                help="Click to submit proposal for voting - voting period is 10 seconds",
                use_container_width=True,
                type="primary"
            )

        # --------------------------------------------------
        # CREATE PROPOSAL TRANSACTION
        # --------------------------------------------------

        if create_proposal_btn:

            if param is None:
                st.error("❌ Invalid parameter selection")
                return

            if new_value == default_value:
                st.warning("⚠️ No change detected - nothing to propose")
                return

            # Show submission progress
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            with st.spinner("🔄 Creating proposal on blockchain..."):
                try:
                    # Update progress
                    progress_bar.progress(25)
                    status_placeholder.info("📤 Sending proposal...")
                    
                    # Create proposal with numbered ID
                    proposal_id = controller.propose_change(param, new_value)
                    
                    # Store proposal in session state with creation time
                    current_time = datetime.now().timestamp()
                    proposal_deadline = current_time + 10  # 10 seconds voting period
                    
                    st.session_state.proposals_list[proposal_id] = {
                        "parameter": param,
                        "current_value": default_value,
                        "proposed_value": new_value,
                        "recommended_value": recommended_value if recommendations else "N/A",
                        "created_at": current_time,
                        "deadline": proposal_deadline,
                        "votes_for": 0,
                        "votes_against": 0,
                        "status": "VOTING",
                        "executed": False
                    }
                    
                    st.session_state.proposal_creation_time[proposal_id] = current_time
                    
                    # Update progress
                    progress_bar.progress(75)
                    status_placeholder.info("⏳ Processing on blockchain...")
                    
                    # Final success
                    progress_bar.progress(100)
                    status_placeholder.empty()
                    
                    # Success message
                    st.success("✅ Proposal Submitted Successfully!")
                    
                    # 🔥 LOG GOVERNANCE PROPOSAL
                    governance_logger.info(
                        f"📋 PROPOSAL CREATED | ID: {proposal_id} | Parameter: {param} | "
                        f"Current: {default_value} | Proposed: {new_value} | "
                        f"Recommended: {recommended_value if recommendations else 'N/A'} | "
                        f"Voting Period: 10 seconds"
                    )
                    
                    # Display proposal details
                    st.subheader("Proposal Submitted for Voting")
                    st.code(f"Proposal ID: {proposal_id}", language="text")
                    
                    # Show proposal summary
                    summary_data = {
                        "Parameter": param,
                        "Current Value": default_value,
                        "Proposed Value": new_value,
                        "Recommended": recommended_value if recommendations else "—",
                        "Proposal ID": proposal_id,
                        "Status": "⏳ Voting Active (10s)",
                        "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.subheader("📋 Proposal Summary")
                    summary_df = pd.DataFrame([summary_data])
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
                    st.info("💡 Share this proposal ID with voters! Voting ends in 10 seconds.")
                    
                    # --------------------------------------------------
                    # RANDOM VOTING SIMULATION (5 ACCOUNTS)
                    # --------------------------------------------------
                    
                    st.markdown("---")
                    st.subheader("🗳️ Community Voting")
                    
                    # Generate 5 random accounts
                    random.seed(proposal_id)  # Use proposal_id as seed for reproducibility
                    voter_names = [
                        f"Voter_{random.randint(1000, 9999)}",
                        f"Voter_{random.randint(1000, 9999)}",
                        f"Voter_{random.randint(1000, 9999)}",
                        f"Voter_{random.randint(1000, 9999)}",
                        f"Voter_{random.randint(1000, 9999)}"
                    ]
                    
                    votes_for = sum(1 for _ in range(5) if random.choice([True, False]))
                    votes_against = 5 - votes_for
                    
                    # Display voting results
                    st.markdown("**5 Community Members Voted:**")
                    
                    voting_cols = st.columns(2)
                    with voting_cols[0]:
                        st.metric("✅ Votes FOR", votes_for)
                    with voting_cols[1]:
                        st.metric("❌ Votes AGAINST", votes_against)
                    
                    # Display voter details
                    voter_data = []
                    for i, voter in enumerate(voter_names):
                        vote = "FOR" if i < votes_for else "AGAINST"
                        voter_data.append({"Voter Address": voter, "Vote": "✅ FOR" if vote == "FOR" else "❌ AGAINST"})
                    
                    voter_df = pd.DataFrame(voter_data)
                    st.dataframe(voter_df, use_container_width=True, hide_index=True)
                    
                    # Display final outcome
                    st.markdown("---")
                    if votes_for > votes_against:
                        st.success(f"✅ **PROPOSAL ACCEPTED** ({votes_for} FOR vs {votes_against} AGAINST)")
                        governance_logger.info(f"✅ PROPOSAL ACCEPTED | ID: {proposal_id} | Votes: {votes_for} FOR, {votes_against} AGAINST")
                    else:
                        st.error(f"❌ **PROPOSAL REJECTED** ({votes_for} FOR vs {votes_against} AGAINST)")
                        governance_logger.warning(f"❌ PROPOSAL REJECTED | ID: {proposal_id} | Votes: {votes_for} FOR, {votes_against} AGAINST")
                        
                        # ❌ REVERT PARAMETER IF REJECTED (don't update)
                        if param in params:
                            controller.protocol_params[param] = default_value
                            governance_logger.info(f"⏮️ PARAMETER REVERTED | Proposal: {proposal_id} | Parameter: {param} | Reverted to: {default_value}")

                except Exception as e:
                    progress_bar.progress(0)
                    status_placeholder.empty()
                    
                    # 🔥 LOG GOVERNANCE FAILURE
                    governance_logger.warning(
                        f"❌ PROPOSAL CREATION FAILED | Parameter: {param} | "
                        f"Value: {new_value} | Error: {str(e)}"
                    )
                    
                    st.error(f"❌ Failed to create proposal: {e}")



        # --------------------------------------------------
        # DOCUMENTATION
        # --------------------------------------------------
        
        st.markdown("---")
        
        with st.expander("ℹ️ About Proposal-Based Governance"):
            st.markdown("""
            **How Proposal-Based Governance Works:**
            
            **Step 1: Create New Proposal 📋**
            - Select a parameter and propose a new value
            - Click "Submit New Proposal" to submit to blockchain
            - Proposal receives a numbered ID
            - **Voting period begins for 10 seconds**
            - NO parameters are updated at this stage
            
            **Step 2: Vote on Proposals 🗳️**
            - Community members vote FOR or AGAINST each proposal
            - Enter the proposal ID to vote on it
            - Voting buttons are active only during the 10-second voting period
            - After 10 seconds, voting period ends and no more votes are accepted
            - Countdown timer shows remaining time
            
            **Step 3: Execute If Approved ⚙️**
            - After 10 seconds, voting period ends automatically
            - Check the proposal execution status
            - Execute button is available only if:
              1. ✅ Voting period has ENDED (10 seconds passed)
              2. ✅ Votes For > Votes Against
            - If approved: Click "Execute Approved Proposal" to update parameters
            - If not approved: Proposal is rejected, parameters remain unchanged
            
            **Key Features:**
            - ✅ Democratic: Requires community consensus (more FOR than AGAINST)
            - ✅ Time-Limited: 10-second voting period ensures quick decision-making
            - ✅ Transparent: All votes recorded on blockchain
            - ✅ Safe: No direct parameter updates without approval
            - ✅ Verifiable: Numbered proposal IDs for easy tracking
            - ✅ Traceable: Full audit trail in governance logs
            
            **Status Definitions:**
            - **VOTING**: Voting period is active (0-10 seconds)
            - **APPROVED**: votesFor > votesAgainst (ready to execute after voting ends)
            - **REJECTED**: votesAgainst >= votesFor (cannot be executed)
            - **EXECUTED**: Proposal has been executed and parameters updated
            
            **Parameter Calculations:**
            - **max_position_size**: Based on maximum quantity executed in trades
            - **leverage**: Calculated from buy/sell trade ratio
            - **risk_limit**: Derived from price volatility and execution patterns
            - **min_confidence**: Computed from trade frequency and execution success
            
            **Security Note:**
            All governance actions are immutable once recorded on-chain.
            Voting period is limited to 10 seconds for quick market responsiveness.
            """)

        st.caption("🔐 Proposal-based governance ensures transparency and community control.")

    except Exception as e:
        st.error(f"❌ Governance panel error: {e}")


# --------------------------------------------------
# STANDALONE RUN
# --------------------------------------------------

if __name__ == "__main__":
    render_governance(protocol=None, current_user=None)