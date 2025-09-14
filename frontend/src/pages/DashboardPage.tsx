import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useProgress } from '../contexts/ProgressContext';
import { ProgressStatistics } from '../components/dashboard/ProgressStatistics';
import { ModuleNavigation } from '../components/dashboard/ModuleNavigation';
import { BookmarkManager } from '../components/dashboard/BookmarkManager';
import { ProgressChart } from '../components/dashboard/ProgressChart';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { modules, userProgress, bookmarks, isLoading } = useProgress();

  const getRecentActivity = () => {
    return Object.values(userProgress)
      .filter(progress => progress.completion_date)
      .sort((a, b) => new Date(b.completion_date!).getTime() - new Date(a.completion_date!).getTime())
      .slice(0, 5);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const recentActivity = getRecentActivity();

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.username}!
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Continue your web development journey with Flask, FastAPI, and PostgreSQL
          </p>
        </div>
      </div>

      {/* Progress Statistics */}
      <ProgressStatistics modules={modules} userProgress={userProgress} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Progress Chart */}
        <div className="lg:col-span-2">
          <ProgressChart modules={modules} userProgress={userProgress} />
        </div>

        {/* Right Column - Bookmarks */}
        <div className="lg:col-span-1">
          <BookmarkManager modules={modules} bookmarks={bookmarks} />
        </div>
      </div>

      {/* Module Navigation */}
      <ModuleNavigation modules={modules} userProgress={userProgress} />

      {/* Recent Activity */}
      {recentActivity.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Recent Activity
            </h3>
            <div className="flow-root">
              <ul className="-mb-8">
                {recentActivity.map((activity, index) => (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      {index !== recentActivity.length - 1 && (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      )}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          </span>
                        </div>
                        <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                          <div>
                            <p className="text-sm text-gray-500">
                              Completed lesson with score of {activity.score}%
                            </p>
                          </div>
                          <div className="text-right text-sm whitespace-nowrap text-gray-500">
                            {new Date(activity.completion_date!).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};