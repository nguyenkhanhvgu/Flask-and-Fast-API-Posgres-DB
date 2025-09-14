import React from 'react';

interface CodeControlsProps {
  onExecute: () => void;
  onValidate?: () => void;
  onToggleHints?: () => void;
  onReset: () => void;
  isExecuting: boolean;
  isValidating: boolean;
  showHints: boolean;
}

const CodeControls: React.FC<CodeControlsProps> = ({
  onExecute,
  onValidate,
  onToggleHints,
  onReset,
  isExecuting,
  isValidating,
  showHints,
}) => {
  return (
    <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {/* Execute Button */}
          <button
            onClick={onExecute}
            disabled={isExecuting || isValidating}
            className={`
              inline-flex items-center px-4 py-2 text-sm font-medium rounded-md
              ${
                isExecuting || isValidating
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500'
              }
            `}
          >
            {isExecuting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running...
              </>
            ) : (
              <>
                <svg className="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m-6-8h8a2 2 0 012 2v8a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2z" />
                </svg>
                Run Code
              </>
            )}
          </button>

          {/* Validate Button (only show if onValidate is provided) */}
          {onValidate && (
            <button
              onClick={onValidate}
              disabled={isExecuting || isValidating}
              className={`
                inline-flex items-center px-4 py-2 text-sm font-medium rounded-md
                ${
                  isExecuting || isValidating
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
                }
              `}
            >
              {isValidating ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Validating...
                </>
              ) : (
                <>
                  <svg className="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Submit Solution
                </>
              )}
            </button>
          )}
        </div>

        <div className="flex items-center space-x-3">
          {/* Hints Button */}
          {onToggleHints && (
            <button
              onClick={onToggleHints}
              className={`
                inline-flex items-center px-3 py-2 text-sm font-medium rounded-md
                ${
                  showHints
                    ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              <svg className="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              {showHints ? 'Hide Hints' : 'Show Hints'}
            </button>
          )}

          {/* Reset Button */}
          <button
            onClick={onReset}
            disabled={isExecuting || isValidating}
            className={`
              inline-flex items-center px-3 py-2 text-sm font-medium rounded-md
              ${
                isExecuting || isValidating
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500'
              }
            `}
          >
            <svg className="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reset
          </button>
        </div>
      </div>
    </div>
  );
};

export default CodeControls;