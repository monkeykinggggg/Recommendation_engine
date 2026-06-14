package org.example.recommendation_system.controller;

import org.example.recommendation_system.external.RecommendationResponse;
import org.example.recommendation_system.model.Product;
import org.example.recommendation_system.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
public class ProductController{

    @Autowired
    private ProductService productService;



    @GetMapping("/products")
    public List<Product> getSampleProducts(){
        return productService.getSeveralRandomProducts();
    }

    @GetMapping("/products/{productId}")
    public Product getProduct(@PathVariable String productId){
        return productService.getProductByparentAsin(productId);
    }

    @GetMapping("/home")
    public RecommendationResponse getHomeRecommendations(){
        return productService.getHomeRecommendationsFromRecommendationEngine();
    }

    @GetMapping("/search")
    public RecommendationResponse getRecommendationsBySearchProducts(@RequestParam("q") String query){
        return productService.searchProductWithRecommendationEngine(query);
    }

    @GetMapping("/products/{productId}/recommendations")
    public RecommendationResponse getProductRecommendations(@PathVariable String productId){
        return productService.getProductRecommendationsFromRecommendationEngine(productId);
    }

}
