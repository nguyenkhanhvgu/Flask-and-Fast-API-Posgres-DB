import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LessonViewer from '../components/lesson/LessonViewer';

const LessonPage: React.FC = () => {
  const { moduleId, lessonId } = useParams<{ moduleId: string; lessonId: string }>();
  const navigate = useNavigate();

  if (!moduleId || !lessonId) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">Invalid lesson URL</div>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const handleLessonChange = (newLessonId: string) => {
    navigate(`/modules/${moduleId}/lessons/${newLessonId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <LessonViewer
        lessonId={lessonId}
        moduleId={moduleId}
        onLessonChange={handleLessonChange}
      />
    </div>
  );
};

export default LessonPage;