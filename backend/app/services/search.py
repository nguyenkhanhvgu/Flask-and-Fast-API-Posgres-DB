"""
Search service for content discovery and filtering.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text, case
from typing import List, Optional, Dict, Any, Tuple
import re
import uuid

from ..models import LearningModule, Lesson, Exercise, UserProgress
from ..schemas import SearchResult, SearchResponse, SearchSuggestion, ContentFilter


class SearchService:
    """Service for handling content search and discovery."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_content(
        self,
        query: Optional[str] = None,
        technology: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        exercise_type: Optional[str] = None,
        completion_status: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> SearchResponse:
        """
        Comprehensive content search with ranking and filtering.
        """
        # Build search results
        results = []
        total_count = 0
        
        # Search modules
        module_results, module_count = self._search_modules(
            query, technology, difficulty_level, user_id, completion_status
        )
        results.extend(module_results)
        total_count += module_count
        
        # Search lessons
        lesson_results, lesson_count = self._search_lessons(
            query, technology, difficulty_level, user_id, completion_status
        )
        results.extend(lesson_results)
        total_count += lesson_count
        
        # Search exercises
        exercise_results, exercise_count = self._search_exercises(
            query, technology, difficulty_level, exercise_type, user_id, completion_status
        )
        results.extend(exercise_results)
        total_count += exercise_count
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Apply pagination
        paginated_results = results[offset:offset + limit]
        
        # Generate suggestions and facets
        suggestions = self._generate_suggestions(query) if query else []
        facets = self._generate_facets(technology, difficulty_level, exercise_type)
        
        return SearchResponse(
            results=paginated_results,
            total_count=total_count,
            query=query,
            filters={
                "technology": technology,
                "difficulty_level": difficulty_level,
                "exercise_type": exercise_type,
                "completion_status": completion_status
            },
            suggestions=suggestions,
            facets=facets
        )
    
    def _search_modules(
        self,
        query: Optional[str],
        technology: Optional[str],
        difficulty_level: Optional[str],
        user_id: Optional[uuid.UUID],
        completion_status: Optional[str]
    ) -> Tuple[List[SearchResult], int]:
        """Search learning modules."""
        base_query = self.db.query(LearningModule)
        
        # Apply filters
        if technology:
            base_query = base_query.filter(LearningModule.technology == technology)
        if difficulty_level:
            base_query = base_query.filter(LearningModule.difficulty_level == difficulty_level)
        
        # Apply completion status filter if user is provided
        if user_id and completion_status:
            # Join with user progress to filter by completion status
            progress_subquery = self.db.query(UserProgress.lesson_id).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.status == completion_status
                )
            ).subquery()
            
            lesson_subquery = self.db.query(Lesson.module_id).filter(
                Lesson.id.in_(self.db.query(progress_subquery.c.lesson_id))
            ).subquery()
            
            base_query = base_query.filter(
                LearningModule.id.in_(self.db.query(lesson_subquery.c.module_id))
            )
        
        # Apply text search with ranking
        if query:
            search_conditions = []
            search_terms = self._extract_search_terms(query)
            
            for term in search_terms:
                search_conditions.extend([
                    LearningModule.name.ilike(f"%{term}%"),
                    LearningModule.description.ilike(f"%{term}%")
                ])
            
            base_query = base_query.filter(or_(*search_conditions))
        
        # Get total count
        total_count = base_query.count()
        
        # Get results with relevance scoring
        modules = base_query.all()
        results = []
        
        for module in modules:
            relevance_score = self._calculate_module_relevance(module, query)
            
            result = SearchResult(
                id=module.id,
                title=module.name,
                description=module.description or "",
                content_type="module",
                technology=module.technology,
                difficulty_level=module.difficulty_level,
                relevance_score=relevance_score,
                url_path=f"/modules/{module.id}"
            )
            results.append(result)
        
        return results, total_count
    
    def _search_lessons(
        self,
        query: Optional[str],
        technology: Optional[str],
        difficulty_level: Optional[str],
        user_id: Optional[uuid.UUID],
        completion_status: Optional[str]
    ) -> Tuple[List[SearchResult], int]:
        """Search lessons."""
        base_query = self.db.query(Lesson).join(LearningModule)
        
        # Apply filters
        if technology:
            base_query = base_query.filter(LearningModule.technology == technology)
        if difficulty_level:
            base_query = base_query.filter(LearningModule.difficulty_level == difficulty_level)
        
        # Apply completion status filter if user is provided
        if user_id and completion_status:
            progress_subquery = self.db.query(UserProgress.lesson_id).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.status == completion_status
                )
            ).subquery()
            
            base_query = base_query.filter(
                Lesson.id.in_(self.db.query(progress_subquery.c.lesson_id))
            )
        
        # Apply text search
        if query:
            search_conditions = []
            search_terms = self._extract_search_terms(query)
            
            for term in search_terms:
                search_conditions.extend([
                    Lesson.title.ilike(f"%{term}%"),
                    Lesson.content.ilike(f"%{term}%")
                ])
            
            base_query = base_query.filter(or_(*search_conditions))
        
        # Get total count
        total_count = base_query.count()
        
        # Get results with relevance scoring
        lessons = base_query.all()
        results = []
        
        for lesson in lessons:
            relevance_score = self._calculate_lesson_relevance(lesson, query)
            
            result = SearchResult(
                id=lesson.id,
                title=lesson.title,
                description=self._extract_description(lesson.content),
                content_type="lesson",
                technology=lesson.module.technology,
                difficulty_level=lesson.module.difficulty_level,
                relevance_score=relevance_score,
                url_path=f"/lessons/{lesson.id}"
            )
            results.append(result)
        
        return results, total_count
    
    def _search_exercises(
        self,
        query: Optional[str],
        technology: Optional[str],
        difficulty_level: Optional[str],
        exercise_type: Optional[str],
        user_id: Optional[uuid.UUID],
        completion_status: Optional[str]
    ) -> Tuple[List[SearchResult], int]:
        """Search exercises."""
        base_query = self.db.query(Exercise).join(Lesson).join(LearningModule)
        
        # Apply filters
        if technology:
            base_query = base_query.filter(LearningModule.technology == technology)
        if difficulty_level:
            base_query = base_query.filter(LearningModule.difficulty_level == difficulty_level)
        if exercise_type:
            base_query = base_query.filter(Exercise.exercise_type == exercise_type)
        
        # Apply completion status filter if user is provided
        if user_id and completion_status:
            progress_subquery = self.db.query(UserProgress.lesson_id).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.status == completion_status
                )
            ).subquery()
            
            base_query = base_query.filter(
                Exercise.lesson_id.in_(self.db.query(progress_subquery.c.lesson_id))
            )
        
        # Apply text search
        if query:
            search_conditions = []
            search_terms = self._extract_search_terms(query)
            
            for term in search_terms:
                search_conditions.extend([
                    Exercise.title.ilike(f"%{term}%"),
                    Exercise.description.ilike(f"%{term}%")
                ])
            
            base_query = base_query.filter(or_(*search_conditions))
        
        # Get total count
        total_count = base_query.count()
        
        # Get results with relevance scoring
        exercises = base_query.all()
        results = []
        
        for exercise in exercises:
            relevance_score = self._calculate_exercise_relevance(exercise, query)
            
            result = SearchResult(
                id=exercise.id,
                title=exercise.title,
                description=exercise.description,
                content_type="exercise",
                technology=exercise.lesson.module.technology,
                difficulty_level=exercise.lesson.module.difficulty_level,
                relevance_score=relevance_score,
                url_path=f"/exercises/{exercise.id}"
            )
            results.append(result)
        
        return results, total_count
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract and clean search terms from query."""
        if not query:
            return []
        
        # Remove special characters and split by whitespace
        cleaned_query = re.sub(r'[^\w\s]', ' ', query.lower())
        terms = [term.strip() for term in cleaned_query.split() if len(term.strip()) > 2]
        
        return terms
    
    def _calculate_module_relevance(self, module: LearningModule, query: Optional[str]) -> float:
        """Calculate relevance score for a module."""
        if not query:
            return 1.0
        
        score = 0.0
        search_terms = self._extract_search_terms(query)
        
        for term in search_terms:
            # Title matches get higher score
            if term in module.name.lower():
                score += 3.0
            
            # Description matches get medium score
            if module.description and term in module.description.lower():
                score += 1.5
            
            # Technology matches get bonus
            if term in module.technology.lower():
                score += 2.0
        
        # Normalize by number of search terms
        if search_terms:
            score = score / len(search_terms)
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _calculate_lesson_relevance(self, lesson: Lesson, query: Optional[str]) -> float:
        """Calculate relevance score for a lesson."""
        if not query:
            return 1.0
        
        score = 0.0
        search_terms = self._extract_search_terms(query)
        
        for term in search_terms:
            # Title matches get higher score
            if term in lesson.title.lower():
                score += 3.0
            
            # Content matches get lower score
            if term in lesson.content.lower():
                score += 1.0
            
            # Technology matches get bonus
            if term in lesson.module.technology.lower():
                score += 2.0
        
        # Normalize by number of search terms
        if search_terms:
            score = score / len(search_terms)
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _calculate_exercise_relevance(self, exercise: Exercise, query: Optional[str]) -> float:
        """Calculate relevance score for an exercise."""
        if not query:
            return 1.0
        
        score = 0.0
        search_terms = self._extract_search_terms(query)
        
        for term in search_terms:
            # Title matches get higher score
            if term in exercise.title.lower():
                score += 3.0
            
            # Description matches get medium score
            if term in exercise.description.lower():
                score += 1.5
            
            # Exercise type matches get bonus
            if term in exercise.exercise_type.lower():
                score += 2.0
            
            # Technology matches get bonus
            if term in exercise.lesson.module.technology.lower():
                score += 2.0
        
        # Normalize by number of search terms
        if search_terms:
            score = score / len(search_terms)
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _extract_description(self, content: str, max_length: int = 200) -> str:
        """Extract a description from content."""
        if not content:
            return ""
        
        # Remove markdown formatting
        cleaned = re.sub(r'[#*`\[\]()]', '', content)
        
        # Take first paragraph or first max_length characters
        first_paragraph = cleaned.split('\n\n')[0]
        
        if len(first_paragraph) <= max_length:
            return first_paragraph.strip()
        
        # Truncate at word boundary
        truncated = first_paragraph[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # If we can find a good break point
            return truncated[:last_space].strip() + "..."
        
        return truncated.strip() + "..."
    
    def _generate_suggestions(self, query: str) -> List[str]:
        """Generate search suggestions based on query."""
        if not query or len(query) < 2:
            return []
        
        suggestions = []
        
        # Get technology suggestions
        tech_results = self.db.query(LearningModule.technology).filter(
            LearningModule.technology.ilike(f"%{query}%")
        ).distinct().limit(3).all()
        
        suggestions.extend([tech[0] for tech in tech_results])
        
        # Get module name suggestions
        module_results = self.db.query(LearningModule.name).filter(
            LearningModule.name.ilike(f"%{query}%")
        ).limit(3).all()
        
        suggestions.extend([name[0] for name in module_results])
        
        # Get lesson title suggestions
        lesson_results = self.db.query(Lesson.title).filter(
            Lesson.title.ilike(f"%{query}%")
        ).limit(3).all()
        
        suggestions.extend([title[0] for title in lesson_results])
        
        return list(set(suggestions))[:5]  # Remove duplicates and limit
    
    def _generate_facets(
        self,
        technology: Optional[str],
        difficulty_level: Optional[str],
        exercise_type: Optional[str]
    ) -> Dict[str, Any]:
        """Generate facets for filtering."""
        facets = {}
        
        # Technology facets
        if not technology:
            tech_facets = self.db.query(
                LearningModule.technology,
                func.count(LearningModule.id).label('count')
            ).group_by(LearningModule.technology).all()
            
            facets['technologies'] = [
                {'value': tech, 'count': count} for tech, count in tech_facets
            ]
        
        # Difficulty level facets
        if not difficulty_level:
            diff_facets = self.db.query(
                LearningModule.difficulty_level,
                func.count(LearningModule.id).label('count')
            ).group_by(LearningModule.difficulty_level).all()
            
            facets['difficulty_levels'] = [
                {'value': diff, 'count': count} for diff, count in diff_facets
            ]
        
        # Exercise type facets
        if not exercise_type:
            type_facets = self.db.query(
                Exercise.exercise_type,
                func.count(Exercise.id).label('count')
            ).group_by(Exercise.exercise_type).all()
            
            facets['exercise_types'] = [
                {'value': ex_type, 'count': count} for ex_type, count in type_facets
            ]
        
        return facets
    
    def get_content_filters(self) -> ContentFilter:
        """Get available filter options."""
        technologies = [tech[0] for tech in self.db.query(LearningModule.technology).distinct().all()]
        difficulty_levels = [diff[0] for diff in self.db.query(LearningModule.difficulty_level).distinct().all()]
        exercise_types = [ex_type[0] for ex_type in self.db.query(Exercise.exercise_type).distinct().all()]
        completion_statuses = ["not_started", "in_progress", "completed"]
        
        return ContentFilter(
            technologies=technologies,
            difficulty_levels=difficulty_levels,
            exercise_types=exercise_types,
            completion_statuses=completion_statuses
        )
    
    def get_autocomplete_suggestions(self, query: str, limit: int = 10) -> List[SearchSuggestion]:
        """Get autocomplete suggestions for search query."""
        if not query or len(query) < 2:
            return []
        
        suggestions = []
        
        # Technology suggestions
        tech_results = self.db.query(
            LearningModule.technology,
            func.count(LearningModule.id).label('count')
        ).filter(
            LearningModule.technology.ilike(f"%{query}%")
        ).group_by(LearningModule.technology).limit(3).all()
        
        for tech, count in tech_results:
            suggestions.append(SearchSuggestion(
                text=tech,
                type="technology",
                count=count
            ))
        
        # Module name suggestions
        module_results = self.db.query(LearningModule.name).filter(
            LearningModule.name.ilike(f"%{query}%")
        ).limit(3).all()
        
        for name in module_results:
            suggestions.append(SearchSuggestion(
                text=name[0],
                type="query",
                count=1
            ))
        
        # Lesson title suggestions
        lesson_results = self.db.query(Lesson.title).filter(
            Lesson.title.ilike(f"%{query}%")
        ).limit(3).all()
        
        for title in lesson_results:
            suggestions.append(SearchSuggestion(
                text=title[0],
                type="query",
                count=1
            ))
        
        return suggestions[:limit]