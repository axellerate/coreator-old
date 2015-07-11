var user_id = $('#user-id').data("user-id");
var first_name = $('#user-first-name').data("first-name");
var last_name = $('#user-last-name').data("last-name");


var SideMenuButtons = React.createClass({
	render: function(){
		return(
			<ul className="nav nav-pills nav-stacked">
			  <li><a href="/projects?page=1"><i className="fa fa-th"></i> Projects</a></li>
			  <li><a href="/people?page=1"><i className="fa fa-users"></i> People</a></li>
			</ul>
		);
	}
});


var SideMenuProfileImage = React.createClass({
	render: function(){
	    return (
	        <div id="side_menu_profile_image"></div>
	    );
	}
});


var SideMenuUserInfo = React.createClass({
	render: function(){
	    return (
	        <div id="side_menu_user_info">
	        	{first_name} {last_name}
	        	<i id="show-user-options-down" className="fa fa-arrow-circle-down"></i>
	        	<i id="show-user-options-up" className="fa fa-arrow-circle-up"></i>
	        </div>
	    );
	}
});

var SideMenuUserOptions = React.createClass({
	render: function(){
	    return (
			<ul className="nav nav-pills nav-stacked user-options">
			  <li><a href={"/profile?id=" + user_id}><i className="fa fa-user"></i> My Profile</a></li>
			  <li><a href={"/user-projects?id=" + user_id}><i className="fa fa-th"></i> My Projects</a></li>
			  <li><a href="/settings"><i className="fa fa-cog"></i> My Settings</a></li>
			  <li><a href="/logout"><i className="fa fa-power-off"></i> Sign Off</a></li>
			</ul>
	    );
	}
});



var SideMenuHeader = React.createClass({


	render: function(){
	    return (
	    	<a href="#profile">
	        	<div id="side_menu_header">
	        		<SideMenuProfileImage />
	        		<SideMenuUserInfo />
	        	</div>
	        </a>
	    );
	}
});


var SideMenu = React.createClass({

	render: function(){
		if(user_id){
			return(
				<div>
					<SideMenuHeader />
					<SideMenuUserOptions />
					<SideMenuButtons />
				</div>
			);
		}else{
			return(
				<div>
					<SideMenuButtons />
				</div>
			);	
		}
	}

});


React.render(
  <SideMenu />,
  document.getElementById("side-menu")
);

$(".user-options").hide();
$("#show-user-options-up").hide();
$("#side_menu_header").click(function(){
	$(".user-options").slideToggle(function(){
		$("#show-user-options-down").fadeToggle(function(){
		});
	});
});
