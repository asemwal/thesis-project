package main

import (
	"log"
	"git.2f30.org/go-mrt.git"
	"flag"
	"fmt"
	"strings"
)

var (
	hpflag = flag.String("host", "localhost:4321", "the host:port to connect to")
	mfflag = flag.String("mrt", "tests/mrt1,tests/mrt2,tests/mrt3", "comma separted list of mrt filenames")
)

type mrtfnames []string

func (m *mrtfnames) String() string {
	return fmt.Sprintf("%v",m)
}

func (m *mrtfnames) Set(val string) error {
	for _, v := range strings.Split(val, ",") {
		*m = append(*m, v)
	}
	return nil
}

func init() {
}
func main() {
	log.Println("init")
	mf, err := mrt.NewMrtFile("./tests/mrt3")
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("mrtfile is :%+v \n",mf)
	dc := make(chan struct{})
	cm, ce := mf.GetChan(dc)
	sum := 0
	for {
		select {
		case dat := <-cm:
			sum++
			if tf, ok := dat.PFunc(); ok {
				//hdr := tf(dat.BGPMsg)
				tf(dat.BGPMsg)
				//fmt.Printf("msg hdr:%v\n", hdr)
				//fmt.Printf("read MRT entry num:%v with header:%v\n", sum, hdr)
			}
		case err = <-ce:
			if err == nil {
				fmt.Println("error was EOF or normal termination nil")
				cm = nil
				ce = nil
			} else {
				fmt.Printf("readall terminated with error:%v\n", err)
			}
		}
		if cm == nil && ce == nil {
			break
		}
	}

}
