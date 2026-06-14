package org.example.recommendation_system.external;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class ProductRecommendation {
    @JsonProperty("parent_asin")
    private String parentAsin;
    @JsonProperty("title")
    private String title;
    @JsonProperty("image_representative")
    private String imageRepresentative;
    @JsonProperty("predicted_score")
    private Double predictedScore;
    @JsonProperty("similarity_score")
    private Double similarityScore;
    @JsonProperty("similar_users_count")
    private Integer similarUsersCount;
}