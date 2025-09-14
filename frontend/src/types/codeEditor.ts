export interface CodeExecutionResult {
  success: boolean;
  output: string;
  error?: string;
  execution_time: number;
  memory_usage?: number;
}

export interface ExerciseValidationResult {
  success: boolean;
  passed_tests: number;
  total_tests: number;
  test_results: TestResult[];
  score: number;
  feedback: string;
}

export interface TestResult {
  name: string;
  passed: boolean;
  expected: any;
  actual: any;
  error?: string;
}

export interface CodeEditorProps {
  initialCode?: string;
  language?: string;
  readOnly?: boolean;
  height?: string;
  exerciseId?: string;
  onCodeChange?: (code: string) => void;
  onExecute?: (result: CodeExecutionResult) => void;
  onValidate?: (result: ExerciseValidationResult) => void;
}

export interface CodeEditorState {
  code: string;
  isExecuting: boolean;
  isValidating: boolean;
  executionResult: CodeExecutionResult | null;
  validationResult: ExerciseValidationResult | null;
  showHints: boolean;
  hints: string[];
}