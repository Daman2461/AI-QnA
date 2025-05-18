import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import Question, RLModelState
from app.core.exceptions import RLModelError

class QAPolicyNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super(QAPolicyNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Softmax(dim=-1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class RLService:
    def __init__(self, db: Session):
        self.db = db
        self.input_size = 10  # Features: confidence_score, feedback_score, etc.
        self.hidden_size = 64
        self.output_size = 3  # Actions: adjust_confidence, adjust_temperature, adjust_context
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize policy network
        self.policy_network = QAPolicyNetwork(
            self.input_size,
            self.hidden_size,
            self.output_size
        ).to(self.device)
        
        self.optimizer = optim.Adam(self.policy_network.parameters())
        self.load_latest_model()

    def load_latest_model(self) -> None:
        """Load the latest active model state from the database."""
        try:
            latest_model = self.db.query(RLModelState).filter(
                RLModelState.is_active == True
            ).order_by(RLModelState.updated_at.desc()).first()

            if latest_model:
                state_dict = latest_model.state_dict
                self.policy_network.load_state_dict(state_dict)
                print(f"Loaded model version {latest_model.version}")
        except Exception as e:
            raise RLModelError(f"Error loading model: {str(e)}")

    def save_model_state(self, metrics: Dict[str, float]) -> None:
        """Save the current model state to the database."""
        try:
            # Create new model state
            model_state = RLModelState(
                model_name="qa_policy_network",
                version=f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                state_dict=self.policy_network.state_dict(),
                metrics=metrics,
                is_active=True
            )

            # Deactivate previous model
            self.db.query(RLModelState).filter(
                RLModelState.is_active == True
            ).update({"is_active": False})

            # Save new model
            self.db.add(model_state)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise RLModelError(f"Error saving model state: {str(e)}")

    def get_state_features(self, question: Question) -> torch.Tensor:
        """Extract features from a question for the RL state."""
        features = [
            question.confidence_score or 0,
            question.feedback_score or 0,
            len(question.question_text) / 100,  # Normalized question length
            len(question.answer_text or "") / 100,  # Normalized answer length
            # Add more features as needed
        ]
        # Pad or truncate to input_size
        features = features[:self.input_size] + [0] * (self.input_size - len(features))
        return torch.FloatTensor(features).to(self.device)

    def get_action(self, state: torch.Tensor) -> Tuple[int, torch.Tensor]:
        """Get action from policy network."""
        with torch.no_grad():
            action_probs = self.policy_network(state)
            action = torch.multinomial(action_probs, 1).item()
        return action, action_probs

    def update_policy(
        self,
        state: torch.Tensor,
        action: int,
        reward: float,
        action_probs: torch.Tensor
    ) -> None:
        """Update policy network using REINFORCE algorithm."""
        try:
            # Calculate loss
            log_prob = torch.log(action_probs[action])
            loss = -log_prob * reward

            # Update policy
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        except Exception as e:
            raise RLModelError(f"Error updating policy: {str(e)}")

    def optimize_response(
        self,
        question: Question,
        current_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize Q&A response using RL."""
        try:
            # Get state features
            state = self.get_state_features(question)

            # Get action from policy
            action, action_probs = self.get_action(state)

            # Apply action to response
            optimized_response = current_response.copy()
            
            if action == 0:  # Adjust confidence
                adjustment = np.random.normal(0, 0.1)  # Small random adjustment
                optimized_response["confidence_score"] = max(0, min(100,
                    int(optimized_response["confidence_score"] * (1 + adjustment))
                ))
            elif action == 1:  # Adjust temperature
                # This would affect the QA chain's temperature
                pass
            elif action == 2:  # Adjust context
                # This would affect how many chunks we use
                pass

            # Calculate reward (this is a simple example)
            reward = 0
            if question.feedback_score:
                reward = question.feedback_score / 100.0

            # Update policy
            self.update_policy(state, action, reward, action_probs)

            # Periodically save model state
            if np.random.random() < 0.1:  # 10% chance to save
                self.save_model_state({
                    "average_reward": reward,
                    "action_distribution": action_probs.tolist()
                })

            return optimized_response

        except Exception as e:
            raise RLModelError(f"Error optimizing response: {str(e)}")

    def train_on_historical_data(self, batch_size: int = 32) -> Dict[str, float]:
        """Train the model on historical question-answer pairs."""
        try:
            # Get historical questions with feedback
            questions = self.db.query(Question).filter(
                Question.feedback_score.isnot(None)
            ).limit(batch_size).all()

            if not questions:
                return {"status": "No training data available"}

            total_reward = 0
            for question in questions:
                state = self.get_state_features(question)
                action, action_probs = self.get_action(state)
                reward = question.feedback_score / 100.0
                self.update_policy(state, action, reward, action_probs)
                total_reward += reward

            # Save model state after training
            metrics = {
                "average_reward": total_reward / len(questions),
                "training_samples": len(questions)
            }
            self.save_model_state(metrics)

            return metrics

        except Exception as e:
            raise RLModelError(f"Error training on historical data: {str(e)}") 