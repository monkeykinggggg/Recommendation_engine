package org.example.recommendation_system.service;

import org.example.recommendation_system.external.ProductRecommendation;
import org.example.recommendation_system.external.RecommendationResponse;
import org.example.recommendation_system.model.Product;
import org.example.recommendation_system.repo.ProductRepo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.List;

@Service
public class ProductService {

    @Autowired
    private ProductRepo productRepo;

    @Value("${fastapi.url}")
    private String fastApiUrl;

    @Autowired
    private RestTemplate restTemplate;

    // Returns username from JWT
    private String getCurrentUserId() {
        String userId = SecurityContextHolder.getContext().getAuthentication().getName();
        System.out.println(userId);
        return userId;
    }

    public Product getProductByparentAsin(String parentAsin){
       getCurrentUserId();
        return productRepo.findByParentAsin(parentAsin);
    }
    public List<Product> getSeveralRandomProducts(){
        return productRepo.findSeveralRandomProducts(20);
    }

    public RecommendationResponse getHomeRecommendationsFromRecommendationEngine(){
        String currentUserId = getCurrentUserId();
        // getting object from fastAPI cast to the defined type in external package
        RecommendationResponse recommendations =  restTemplate.getForObject(fastApiUrl+"/recommendations/enhanced/"+currentUserId, RecommendationResponse.class);
        System.out.println(recommendations.getAlgorithm());
        ProductRecommendation firstProduct = recommendations.getRecommendations().get(0);
        System.out.println(firstProduct.getImageRepresentative());
        return recommendations;
    }

    public RecommendationResponse searchProductWithRecommendationEngine(String query){
        String currentUserId = getCurrentUserId();
        String queryUrl = UriComponentsBuilder
                .fromUriString(fastApiUrl+"/search/"+currentUserId)
                .queryParam("q", query)
                .toUriString();
        System.out.println("Calling fastAPI endpoint: "+queryUrl);
        return restTemplate.getForObject(queryUrl, RecommendationResponse.class);
    }

    public RecommendationResponse getProductRecommendationsFromRecommendationEngine(String productId) {
        String currentUserId = getCurrentUserId();
        String url = fastApiUrl + "/recommendations/content-based/" + currentUserId + "/" + productId;
        RecommendationResponse response =  restTemplate.getForObject(url, RecommendationResponse.class);
        ProductRecommendation firstProduct = response.getRecommendations().get(0);
        System.out.println(firstProduct.getImageRepresentative());
        return response;
    }
}
