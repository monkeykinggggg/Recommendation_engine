package org.example.recommendation_system.controller;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {

    @GetMapping("/hello")
    public String hello(HttpServletRequest request){

        return "hello world "+request.getSession().getId();
    }

    @GetMapping("/about")
    public String about(HttpServletRequest request){

        return "Asia's website "+request.getSession().getId();
    }
}
