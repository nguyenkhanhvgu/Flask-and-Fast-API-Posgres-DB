import React, { useState } from 'react';
import { CodeEditor } from './index';
import { CodeExecutionResult, ExerciseValidationResult } from '../../types/codeEditor';

const CodeEditorExample: React.FC = () => {
  const [executionResult, setExecutionResult] = useState<CodeExecutionResult | null>(null);
  const [validationResult, setValidationResult] = useState<ExerciseValidationResult | null>(null);

  const handleCodeChange = (code: string) => {
    console.log('Code changed:', code);
  };

  const handleExecute = (result: CodeExecutionResult) => {
    setExecutionResult(result);
    console.log('Execution result:', result);
  };

  const handleValidate = (result: ExerciseValidationResult) => {
    setValidationResult(result);
    console.log('Validation result:', result);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Code Editor Examples</h1>
      
      {/* Basic Code Editor */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Basic Code Editor</h2>
        <CodeEditor
          initialCode={`# Welcome to the Python code editor!
print("Hello, World!")

# Try writing some code and click 'Run Code'
def greet(name):
    return f"Hello, {name}!"

print(greet("Developer"))`}
          language="python"
          height="300px"
          onCodeChange={handleCodeChange}
          onExecute={handleExecute}
        />
      </div>

      {/* Exercise Code Editor */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Exercise Code Editor</h2>
        <div className="bg-blue-50 p-4 rounded-lg mb-4">
          <h3 className="font-medium text-blue-900 mb-2">Exercise: Sum of Two Numbers</h3>
          <p className="text-blue-800 text-sm">
            Write a function called <code className="bg-blue-100 px-1 rounded">add_numbers</code> that takes two parameters 
            and returns their sum. The function should handle both integers and floating-point numbers.
          </p>
        </div>
        <CodeEditor
          initialCode={`def add_numbers(a, b):
    # Your code here
    pass

# Test your function
result = add_numbers(5, 3)
print(f"5 + 3 = {result}")`}
          language="python"
          height="250px"
          exerciseId="example-exercise-1"
          onCodeChange={handleCodeChange}
          onExecute={handleExecute}
          onValidate={handleValidate}
        />
      </div>

      {/* Read-only Code Editor */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Read-only Code Display</h2>
        <CodeEditor
          initialCode={`# This is a read-only code example
class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def get_history(self):
        return self.history

# Usage example
calc = Calculator()
print(calc.add(10, 5))
print(calc.get_history())`}
          language="python"
          height="300px"
          readOnly={true}
        />
      </div>

      {/* Results Display */}
      {(executionResult || validationResult) && (
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Latest Results</h2>
          
          {executionResult && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">Execution Result:</h3>
              <div className="bg-gray-100 p-3 rounded text-sm">
                <div><strong>Success:</strong> {executionResult.success ? 'Yes' : 'No'}</div>
                <div><strong>Execution Time:</strong> {executionResult.execution_time}s</div>
                {executionResult.output && <div><strong>Output:</strong> {executionResult.output}</div>}
                {executionResult.error && <div><strong>Error:</strong> {executionResult.error}</div>}
              </div>
            </div>
          )}

          {validationResult && (
            <div>
              <h3 className="font-medium text-gray-700 mb-2">Validation Result:</h3>
              <div className="bg-gray-100 p-3 rounded text-sm">
                <div><strong>Success:</strong> {validationResult.success ? 'Yes' : 'No'}</div>
                <div><strong>Score:</strong> {validationResult.score}%</div>
                <div><strong>Tests Passed:</strong> {validationResult.passed_tests}/{validationResult.total_tests}</div>
                {validationResult.feedback && <div><strong>Feedback:</strong> {validationResult.feedback}</div>}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CodeEditorExample;