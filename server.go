/**
* Copyright © 2017, ACM@UIUC
*
* This file is part of the ACM GPU Cluster Project.
*
* The ACM GPU Cluster Project is open source software, released under
* the University of Illinois/NCSA Open Source License. You should have
* received a copy of this license in a file with the distribution.
**/

package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/acm-uiuc/gpu-cluster-backend/config"
	"github.com/acm-uiuc/gpu-cluster-backend/routes"
	"github.com/acm-uiuc/gpu-cluster-backend/router"
)

func main() {
	router := router.NewRouter((routes.APIRoutes))
	log.Fatal(http.ListenAndServe(":"+fmt.Sprintf("%d", config.API_PORT), router))
}