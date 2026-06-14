package org.example.recommendation_system.external;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import java.util.List;

@Data
public class RecommendationResponse {
    @JsonProperty("user_id")
    private String userId;
    @JsonProperty("algorithm")
    private String algorithm;
    @JsonProperty("recommendations")
    private List<ProductRecommendation> recommendations;
}
