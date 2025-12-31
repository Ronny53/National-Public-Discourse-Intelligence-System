from typing import List, Dict, Any
from backend.api.schemas.social_data import SocialPost
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

class IssueClusterer:
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=1000, 
            ngram_range=(1, 2) # Bigrams for better context
        )

    def cluster_issues(self, posts: List[SocialPost]) -> List[Dict[str, Any]]:
        """
        Clusters posts into issues and returns summary of each cluster.
        """
        if not posts or len(posts) < self.n_clusters:
            return []

        texts = [f"{p.title} {p.text}" for p in posts]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
            kmeans.fit(tfidf_matrix)
            
            cluster_labels = kmeans.labels_
            feature_names = self.vectorizer.get_feature_names_out()
            ordered_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
            
            clusters = []
            for i in range(self.n_clusters):
                # Get top keywords for this cluster
                top_features = [feature_names[ind] for ind in ordered_centroids[i, :5]]
                
                # Count size
                size = np.sum(cluster_labels == i)
                
                clusters.append({
                    "cluster_id": i,
                    "top_keywords": top_features,
                    "size": int(size),
                    "label": f"Issue: {', '.join(top_features[:3])}" # Auto-label
                })
                
            return sorted(clusters, key=lambda x: x['size'], reverse=True)
            
        except Exception as e:
            # Fallback for very small datasets or errors
            print(f"Clustering error: {e}")
            return []
