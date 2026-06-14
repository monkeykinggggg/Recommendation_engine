package org.example.recommendation_system.model;

import lombok.Data;
import org.springframework.data.neo4j.core.schema.*;

import java.util.List;

@Node("Product")
@Data
public class Product {
    @Id
    @Property("parent_asin")
    String parentAsin;

    @Property("rating_number")
    Integer ratingNumber;
    @Property("average_rating")
    Double averageRating;

    @Property("title")
    String title;

    @Property("store")
    String store;
    @Property("images")
    List<String> images;

    @Property("features")
    List<String> features;

    @Property("description")
    List<String> descriptions;
}
