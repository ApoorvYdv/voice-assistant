import { Bot, Wrench, Zap, User, AlertCircle } from 'lucide-react';
import { FC } from 'react';

// Define the structure of a single step in the flow
export type FlowStep = {
  type: 'user_message' | 'agent_step' | 'error';
  data: any;
};

// A mapping of step types to icons and styles
const stepConfig = {
  llm_response: { icon: Bot, color: 'text-blue-400' },
  tool_call: { icon: Wrench, color: 'text-yellow-400' },
  tool_result: { icon: Zap, color: 'text-green-400' },
  user_message: { icon: User, color: 'text-purple-400' },
  error: { icon: AlertCircle, color: 'text-red-500' },
};

const Step: FC<{ stepData: any }> = ({ stepData }) => {
  const stepType = Object.keys(stepData)[0]; // e.g., 'llm_response', 'tool_call'
  
  // Determine the primary step key ('llm_response', 'tool_call', etc.)
  const primaryKey = stepData.tool_name ? (stepData.tool_output ? 'tool_result' : 'tool_call') : 'llm_response';
  const config = stepConfig[primaryKey];
  
  const renderContent = () => {
    if (primaryKey === 'tool_call') {
      return `Calling tool: ${stepData.tool_name}(${JSON.stringify(stepData.tool_args)})`;
    }
    if (primaryKey === 'tool_result') {
      return `Tool returned: "${stepData.tool_output}"`;
    }
    return stepData.text;
  };
  
  return (
    <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg animate-fade-in-up">
      <div className={`flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center ${config.color}`}>
        <config.icon size={18} />
      </div>
      <div className="flex-grow pt-1 text-gray-300">
        <p>{renderContent()}</p>
      </div>
    </div>
  );
};

const AgentFlowDisplay: FC<{ steps: FlowStep[] }> = ({ steps }) => {
  if (steps.length === 0) {
    return (
        <div className="h-48 flex items-center justify-center text-gray-500">
            <p>I'm ready. Click the mic to start.</p>
        </div>
    );
  }

  return (
    <div className="h-48 overflow-y-auto pr-2 space-y-3">
      {steps.map((step, index) => {
        if (step.type === 'user_message') {
            const config = stepConfig.user_message;
            return (
                <div key={index} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg animate-fade-in-up">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center ${config.color}`}>
                        <config.icon size={18} />
                    </div>
                    <p className="flex-grow pt-1.5 text-gray-300 font-semibold italic">"{step.data.text}"</p>
                </div>
            )
        }
        if (step.type === 'agent_step') {
            return <Step key={index} stepData={step.data} />;
        }
        if (step.type === 'error') {
            const config = stepConfig.error;
            return (
                <div key={index} className="flex items-start gap-3 p-3 bg-red-900/50 rounded-lg animate-fade-in-up">
                     <div className={`flex-shrink-0 w-8 h-8 rounded-full bg-red-800 flex items-center justify-center ${config.color}`}>
                        <config.icon size={18} />
                    </div>
                    <p className="flex-grow pt-1.5 text-red-300">{step.data.text}</p>
                </div>
            )
        }
        return null;
      })}
    </div>
  );
};

export default AgentFlowDisplay;