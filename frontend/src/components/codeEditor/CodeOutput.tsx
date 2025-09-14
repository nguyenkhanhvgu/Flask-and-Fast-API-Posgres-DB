import React from 'react';
import { CodeExecutionResult } from '../../types/codeEditor';

interface CodeOutputProps {
  result: CodeExecutionResult;
}

const CodeOutput: React.FC<CodeOutputProps> = ({ result }) => {
  const formatExecutionTime = (time: number) => {
    if (time < 1) {
      return `${(time * 1000).toFixed(0)}ms`;
    }
    return `${time.toFixed(2)}s`;
  };

  const formatMemoryUsage = (memory?: number) => {
    if (!memory) return null;
    if (memory < 1024) {
      return `${memory.toFixed(0)}B`;
    } else if (memory < 1024 * 1024) {
      return `${(memory / 1024).toFixed(1)}KB`;
    } else {
      return `${(memory / (1024 * 1024)).toFixed(1)}MB`;
    }
  };

  return (
    <div className="border-t border-gray-200">
      {/* Output Header */}
      <div className={`px-4 py-2 ${result.success ? 'bg-green-50' : 'bg-red-50'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {result.success ? (
              <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="h-4 w-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            <span className={`text-sm font-medium ${result.success ? 'text-green-800' : 'text-red-800'}`}>
              {result.success ? 'Execution Successful' : 'Execution Failed'}
            </span>
          </div>
          
          <div className="flex items-center space-x-4 text-xs text-gray-600">
            <span>Time: {formatExecutionTime(result.execution_time)}</span>
            {result.memory_usage && (
              <span>Memory: {formatMemoryUsage(result.memory_usage)}</span>
            )}
          </div>
        </div>
      </div>

      {/* Output Content */}
      <div className="p-4">
        {result.output && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Output:</h4>
            <pre className="bg-gray-900 text-green-400 p-3 rounded-md text-sm overflow-x-auto whitespace-pre-wrap font-mono">
              {result.output}
            </pre>
          </div>
        )}

        {result.error && (
          <div>
            <h4 className="text-sm font-medium text-red-700 mb-2">Error:</h4>
            <pre className="bg-red-50 text-red-800 p-3 rounded-md text-sm overflow-x-auto whitespace-pre-wrap font-mono border border-red-200">
              {result.error}
            </pre>
          </div>
        )}

        {!result.output && !result.error && result.success && (
          <div className="text-sm text-gray-500 italic">
            Code executed successfully with no output.
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeOutput;