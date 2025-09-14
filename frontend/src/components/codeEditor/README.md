# Code Editor Component

A comprehensive interactive code editor component built with Monaco Editor for the Web Frameworks Tutorial Platform.

## Features

- **Monaco Editor Integration**: Full-featured code editor with Python syntax highlighting
- **Code Execution**: Execute code remotely with real-time output display
- **Exercise Validation**: Submit and validate coding exercises with detailed feedback
- **Hints System**: Progressive hints for coding exercises
- **Error Handling**: Comprehensive error display and handling
- **Responsive Design**: Works across different screen sizes
- **Read-only Mode**: Display code examples without editing capabilities

## Components

### CodeEditor (Main Component)

The primary component that orchestrates all functionality.

**Props:**
- `initialCode?: string` - Initial code to display
- `language?: string` - Programming language (default: 'python')
- `readOnly?: boolean` - Whether the editor is read-only
- `height?: string` - Height of the editor (default: '400px')
- `exerciseId?: string` - ID for exercise validation
- `onCodeChange?: (code: string) => void` - Callback when code changes
- `onExecute?: (result: CodeExecutionResult) => void` - Callback after code execution
- `onValidate?: (result: ExerciseValidationResult) => void` - Callback after exercise validation

### CodeControls

Control buttons for code execution, validation, hints, and reset.

### CodeOutput

Displays code execution results including output, errors, and performance metrics.

### ValidationResults

Shows exercise validation results with test outcomes, scores, and feedback.

## Usage Examples

### Basic Code Editor

```tsx
import { CodeEditor } from './components/codeEditor';

function MyComponent() {
  return (
    <CodeEditor
      initialCode="print('Hello, World!')"
      language="python"
      height="300px"
      onCodeChange={(code) => console.log('Code changed:', code)}
    />
  );
}
```

### Exercise Code Editor

```tsx
import { CodeEditor } from './components/codeEditor';

function ExerciseComponent() {
  const handleValidation = (result) => {
    if (result.success) {
      console.log('Exercise completed!');
    } else {
      console.log('Try again:', result.feedback);
    }
  };

  return (
    <CodeEditor
      initialCode="def add_numbers(a, b):\n    # Your code here\n    pass"
      exerciseId="exercise-123"
      onValidate={handleValidation}
    />
  );
}
```

### Read-only Code Display

```tsx
import { CodeEditor } from './components/codeEditor';

function CodeExample() {
  return (
    <CodeEditor
      initialCode="# This is a code example\nprint('Read-only code')"
      readOnly={true}
      height="200px"
    />
  );
}
```

## API Integration

The component integrates with the backend API through the following endpoints:

- `POST /api/v1/code/execute` - Execute code
- `POST /api/v1/exercises/validate` - Validate exercise solutions
- `GET /api/v1/exercises/{id}/hints` - Get exercise hints

## Types

### CodeExecutionResult

```typescript
interface CodeExecutionResult {
  success: boolean;
  output: string;
  error?: string;
  execution_time: number;
  memory_usage?: number;
}
```

### ExerciseValidationResult

```typescript
interface ExerciseValidationResult {
  success: boolean;
  passed_tests: number;
  total_tests: number;
  test_results: TestResult[];
  score: number;
  feedback: string;
}
```

### TestResult

```typescript
interface TestResult {
  name: string;
  passed: boolean;
  expected: any;
  actual: any;
  error?: string;
}
```

## Styling

The component uses Tailwind CSS for styling and follows the design system of the tutorial platform. Key design elements:

- Clean, modern interface with rounded corners and shadows
- Color-coded feedback (green for success, red for errors, yellow for warnings)
- Responsive layout that works on mobile and desktop
- Accessible design with proper contrast and focus states

## Testing

Comprehensive test suite covering:

- Component rendering and props
- User interactions (code editing, button clicks)
- API integration and error handling
- State management and callbacks
- Accessibility and responsive behavior

Run tests with:
```bash
npm test src/components/codeEditor
```

## Performance Considerations

- Monaco Editor is loaded asynchronously to reduce initial bundle size
- Code execution is debounced to prevent excessive API calls
- Results are cached to improve user experience
- Memory usage is monitored and displayed when available

## Accessibility

- Keyboard navigation support
- Screen reader compatible
- High contrast mode support
- Focus management for modal dialogs and popups
- ARIA labels and descriptions for interactive elements

## Browser Support

- Modern browsers with ES2018+ support
- Monaco Editor requirements: Chrome 63+, Firefox 58+, Safari 11+, Edge 79+
- Graceful degradation for older browsers with fallback text editor