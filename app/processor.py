import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from .database.operations import DatabaseOperations
from .subtitle import SubtitleExtractor
from .movie_name import MovieNameRecognizer
from .metadata import MetadataFetcher

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, db_ops: DatabaseOperations):
        self.db_ops = db_ops
        self.subtitle_extractor = SubtitleExtractor()
        self.movie_name_recognizer = MovieNameRecognizer()
        self.metadata_fetcher = MetadataFetcher()

    def process_video(self, file_path: str) -> Optional[Dict[str, Any]]:
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            # Get original name from file path
            original_name = Path(file_path).stem

            # Recognize official movie name
            official_name = self.movie_name_recognizer.recognize(original_name)
            if not official_name:
                logger.warning(f"Could not recognize official name for: {original_name}")
                official_name = original_name

            # Create video entry in database
            video = self.db_ops.create_video(
                file_path=file_path,
                original_name=original_name,
                official_name=official_name
            )

            # Extract subtitles
            subtitle_results = self.subtitle_extractor.extract_all(file_path)
            for sub_result in subtitle_results:
                self.db_ops.add_subtitle(
                    video_id=video.id,
                    language=sub_result['language'],
                    source_type=sub_result['source_type'],
                    content_path=sub_result['content_path']
                )

            # Fetch metadata
            metadata = self.metadata_fetcher.fetch_metadata(official_name)
            if metadata:
                # Update movie info
                self.db_ops.update_movie_info(
                    video_id=video.id,
                    title=metadata.get('title'),
                    original_title=metadata.get('original_title'),
                    release_date=metadata.get('release_date'),
                    runtime=metadata.get('runtime'),
                    overview=metadata.get('overview'),
                    poster_path=metadata.get('poster_path'),
                    tmdb_id=metadata.get('tmdb_id'),
                    imdb_id=metadata.get('imdb_id')
                )

                # Add genres
                if 'genres' in metadata:
                    self.db_ops.add_genres_to_video(video.id, metadata['genres'])

                # Add actors
                if 'actors' in metadata:
                    self.db_ops.add_actors_to_video(video.id, metadata['actors'])

            return {
                'id': video.id,
                'original_name': original_name,
                'official_name': official_name,
                'subtitles': subtitle_results,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Error processing video {file_path}: {str(e)}")
            return None

    def batch_process_videos(self, video_paths: List[str]) -> List[Dict[str, Any]]:
        results = []
        for path in video_paths:
            result = self.process_video(path)
            if result:
                results.append(result)
            else:
                results.append({'error': f'Failed to process {path}'})
        return results 