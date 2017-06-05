/**
* Copyright © 2017, ACM@UIUC
*
* This file is part of the ACM GPU Cluster Project.
*
* The ACM GPU Cluster Project is open source software, released under
* the University of Illinois/NCSA Open Source License. You should have
* received a copy of this license in a file with the distribution.
**/

package server

import (
	"net/http"

	"github.com/acm-uiuc/gpu-cluster-backend/config"
	"github.com/acm-uiuc/gpu-cluster-backend/routes"
	"github.com/gorilla/mux"
)

func NewRouter(routes routes.RouteCollection) *mux.Router {

	router := mux.NewRouter()
	for _, route := range routes {
		var handler http.Handler

		handler = route.HandlerFunc
		//Log request
		handler = logger(handler, route.Name)

		router.
			Methods(route.Method).
			Path(route.Pattern).
			Name(route.Name).
			Handler(handler)

	}
	router.PathPrefix("/").Handler(http.FileServer(http.Dir("./")))
	return router
}