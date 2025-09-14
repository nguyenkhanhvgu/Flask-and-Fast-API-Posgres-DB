import React, { useState, useCallback, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { apiClient } from '../../services/api';
import {
  CodeEditorProps,
  CodeEditorState,
  CodeExecutionResult,
  ExerciseValidationResult,
} from '../../types/codeEditor';
import CodeOutput from './CodeOutput';
import CodeControls from './CodeControls';
import ValidationResults from './ValidationResults';

const CodeEditor: React.FC<CodeEditorProps> = ({
  initialCode = '',
  language = 'python',
  readOnly = false,
  height = '400px',
  exerciseId,
  onCodeChange,
  onExecute,
  onValidate,
}) => {
  const [state, setState] = useState<CodeEditorState>({
    code: initialCode,
    isExecuting: false,
    isValidating: false,
    executionResult: null,
    validationResult: null,
    showHints: false,
    hints: [],
  });

  // Load hints if exerciseId is provided
  useEffect(() => {
    if (exerciseId) {
      loadHints();
    }
  }, [exerciseId]);

  const loadHints = async () => {
    if (!exerciseId) return;
    
    try {
      const hints = await apiClient.getExerciseHints(exerciseId);
      setState(prev => ({ ...prev, hints }));
    } catch (error) {
      console.error('Failed to load hints:', error);
    }
  };

  const handleCodeChange = useCallback((value: string | undefined) => {
    const newCode = value || '';
    setState(prev => ({ ...prev, code: newCode }));
    onCodeChange?.(newCode);
  }, [onCodeChange]);

  const executeCode = async () => {
    setState(prev => ({ ...prev, isExecuting: true, executionResult: null }));
    
    try {
      const result: CodeExecutionResult = await apiClient.executeCode(state.code, language);
      setState(prev => ({ ...prev, executionResult: result }));
      onExecute?.(result);
    } catch (error) {
      const errorResult: CodeExecutionResult = {
        success: false,
        output: '',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        execution_time: 0,
      };
      setState(prev => ({ ...prev, executionResult: errorResult }));
      onExecute?.(errorResult);
    } finally {
      setState(prev => ({ ...prev, isExecuting: false }));
    }
  };

  const validateExercise = async () => {
    if (!exerciseId) return;
    
    setState(prev => ({ ...prev, isValidating: true, validationResult: null }));
    
    try {
      const result: ExerciseValidationResult = await apiClient.validateExercise(exerciseId, state.code);
      setState(prev => ({ ...prev, validationResult: result }));
      onValidate?.(result);
    } catch (error) {
      const errorResult: ExerciseValidationResult = {
        success: false,
        passed_tests: 0,
        total_tests: 0,
        test_results: [],
        score: 0,
        feedback: error instanceof Error ? error.message : 'Validation failed',
      };
      setState(prev => ({ ...prev, validationResult: errorResult }));
      onValidate?.(errorResult);
    } finally {
      setState(prev => ({ ...prev, isValidating: false }));
    }
  };

  const toggleHints = () => {
    setState(prev => ({ ...prev, showHints: !prev.showHints }));
  };

  const resetCode = () => {
    setState(prev => ({ 
      ...prev, 
      code: initialCode,
      executionResult: null,
      validationResult: null,
    }));
    onCodeChange?.(initialCode);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Editor Header */}
      <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-700">Code Editor</h3>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500 capitalize">{language}</span>
            {readOnly && (
              <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">
                Read Only
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Monaco Editor */}
      <div className="relative">
        <Editor
          height={height}
          language={language}
          value={state.code}
          onChange={handleCodeChange}
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            wordWrap: 'on',
            theme: 'vs-light',
          }}
          loading={
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          }
        />
      </div>

      {/* Controls */}
      {!readOnly && (
        <CodeControls
          onExecute={executeCode}
          onValidate={exerciseId ? validateExercise : undefined}
          onToggleHints={state.hints && state.hints.length > 0 ? toggleHints : undefined}
          onReset={resetCode}
          isExecuting={state.isExecuting}
          isValidating={state.isValidating}
          showHints={state.showHints}
        />
      )}

      {/* Hints */}
      {state.showHints && state.hints && state.hints.length > 0 && (
        <div className="bg-yellow-50 border-t border-yellow-200 p-4">
          <h4 className="text-sm font-medium text-yellow-800 mb-2">Hints:</h4>
          <ul className="space-y-1">
            {state.hints.map((hint, index) => (
              <li key={index} className="text-sm text-yellow-700">
                {index + 1}. {hint}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Output */}
      {state.executionResult && (
        <CodeOutput result={state.executionResult} />
      )}

      {/* Validation Results */}
      {state.validationResult && (
        <ValidationResults result={state.validationResult} />
      )}
    </div>
  );
};

export default CodeEditor;